import asyncio
import json
import os
import string
import secrets
from operator import attrgetter, itemgetter
from uuid import uuid4

from devtools import debug
from eth_account import Account
from sqlalchemy import select
from web3 import Web3
from web3.middleware import geth_poa_middleware
from invoke import task
from loguru import logger

from app.config import get_settings
from app.db import db_client, parties, invoices, orders
from app.main import startup
from app.blockchain import blockchain_client
from app.schemas import TransactionGet, TransactionInputGet, TransactionEventGet
from .utils import run_command
from app.contracts import ERC1155Contract, InvoiceRegistryContract


# https://docs.microsoft.com/en-us/azure/developer/python/configure-local
# -development-environment?tabs=bash


@task
def runapp(c):
    c.run('uvicorn app.main:app --reload')


@task
def password_gen(c, length=16):
    alphabet = string.ascii_letters + string.digits
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and sum(c.isdigit() for c in password) >= 3):
            break
    print(password)


@task
def clientsdk_generate(c):
    c.run(
        'openapi-python-client generate '
        '--url http://127.0.0.1:8000/openapi.json'
    )


@task
def clientsdk_update(c):
    c.run(
        'openapi-python-client update '
        '--url http://127.0.0.1:8000/openapi.json'
    )


@task
def export_requirements(c):
    command = 'poetry export ' \
              '--format requirements.txt ' \
              '--without-hashes ' \
              '--output requirements.txt'
    run_command(command, c, logger)


def create_w3() -> Web3:
    url = os.getenv("chainvoice_qnode_url")
    access_key = os.getenv("chainvoice_qnode_key")
    w3 = Web3(Web3.HTTPProvider(f'{url}/{access_key}'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print(f'connected: {w3.isConnected()}')
    return w3


def create_w3_local() -> Web3:
    url = 'http://localhost:8545'
    w3 = Web3(Web3.HTTPProvider(url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print(f'connected: {w3.isConnected()}')
    return w3


def create_erc1155(w3):
    with open('build/contracts/ChainvoiceERC1155.json') as f:
        compiled_contract = json.load(f)
        contract_abi = compiled_contract['abi']
        assert contract_abi
    contract_address = os.getenv('chainvoice_erc1155_contract_address')
    erc1155 = ERC1155Contract(w3, contract_address, contract_abi)
    return erc1155


def create_invoice_registry(w3):
    with open('build/contracts/InvoiceRegistry.json') as f:
        compiled_contract = json.load(f)
        contract_abi = compiled_contract['abi']
        assert contract_abi
    contract_address = os.getenv('chainvoice_invoice_registry_contract_address')
    contract = InvoiceRegistryContract(w3, contract_address, contract_abi)
    return contract


@task
def read_blocks(c):
    w3 = create_w3()
    erc1155 = create_erc1155(w3)
    invoice_registry = create_invoice_registry(w3)
    last_block_number = w3.eth.block_number()
    # print(f'last block: {last_block_number}')
    # block_num = last_block_number
    # for i in range(5):
    #     tx_count = 0
    #     while tx_count == 0:
    #         tx_count = w3.eth.getBlockTransactionCount(block_num)
    #         block_num -= 1
    #     print(f'block: {block_num}, txs: {tx_count}')
    #     if block_num == -1:
    #         break
    # print('done!')
    # block = w3.eth.getBlock(last_block_number-10)
    # debug(block)
    # debug(tx)
    # tx_count = w3.eth.getBlockTransactionCount(tx.blockNumber)
    # print(f'tx count {tx_count}')
    paid_events = invoice_registry.contract.events.InvoicePaid.createFilter(
        fromBlock=0, toBlock=last_block_number).get_all_entries()
    transfer_events = erc1155.contract.events.TransferSingle.createFilter(
        fromBlock=0, toBlock=last_block_number).get_all_entries()
    entries = []
    for event in paid_events:
        tx_hash = event.transactionHash
        tx = w3.eth.getTransaction(tx_hash)
        tx_input = erc1155.contract.decode_function_input(tx.input)
        tx_args = tx_input[1]
        tx_args['data'] = Web3.toHex(tx_input[1]['data'])
        paid_event_entry = {
            'name': event.event,
            'args': dict(event.args),
            'address': event.address,
            'log_index': event.logIndex
        }
        paid_event_entry['args']['invoiceId'] = Web3.toHex(event.args.invoiceId)
        transfer_event_entries = [
            {
                'name': event.event,
                'args': dict(event.args),
                'address': event.address,
                'log_index': event.logIndex
            } for event in transfer_events if event.transactionHash == tx_hash
        ]
        tx_entry = TransactionGet(
            hash=Web3.toHex(tx_hash),
            block_number=tx.blockNumber,
            index_in_block=tx.transactionIndex,
            from_address=tx['from'],
            to_address=tx['to'],
            input={
                'contract': 'ChainvoiceERC1155',
                'address': tx_input[0].address,
                'function': str(tx_input[0]),
                'args': tx_args
            },
            events=sorted([
                paid_event_entry,
                *transfer_event_entries
            ], key=itemgetter('log_index'))
        )
        entries.append(tx_entry)
    entries.sort(
        key=attrgetter('block_number', 'index_in_block'), reverse=True
    )
    debug(entries)


@task
def token_transfer(c):
    w3 = create_w3()
    erc1155 = create_erc1155(w3)
    owner_key = os.getenv('chainvoice_qadmin_private_key')
    owner = Account.from_key(owner_key)
    other_address = os.getenv('chainvoice_other_address')
    token_id = 0
    transfer_amount = 1_000
    txn_receipt = erc1155.safe_transfer_from(
        owner, owner.address, other_address,
        token_id, transfer_amount, b'initial amount'
    )
    print(f'txn_receipt: {txn_receipt}')
    print(f"transaction status: {txn_receipt['status']}")
    print(f'owner has: {erc1155.balance_of(owner.address, token_id)}')
    print(f'other has: {erc1155.balance_of(other_address, token_id)}')


@task
def invoice_register(c):
    w3 = create_w3()
    contract = create_invoice_registry(w3)
    owner_key = os.getenv('chainvoice_qadmin_private_key')
    owner = Account.from_key(owner_key)
    debug(w3.eth.getBalance(owner.address))
    other_address = os.getenv('chainvoice_other_address')
    debug(owner.address)
    debug(other_address)
    invoice_id = uuid4().int
    token_id = 1
    invoice_amount = 1000
    contract_call = contract.contract.functions.registerInvoice1(
        invoice_id, other_address, token_id, invoice_amount
    )
    nonce = w3.eth.getTransactionCount(owner.address)
    txn = contract_call.buildTransaction({
        'nonce': nonce,
        'gas': 1000000,
    })
    signed_txn = w3.eth.account.sign_transaction(
        txn, private_key=owner.key
    )
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.waitForTransactionReceipt(txn_hash)
    debug(invoice_id)
    print(f'txn_receipt: {txn_receipt}')
    print(f"transaction status: {txn_receipt['status']}")
    debug(contract.contract.functions.invoices(invoice_id).call())


@task
def test_invoice_lifecycle(c):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_test_invoice_lifecycle())


async def _test_invoice_lifecycle():
    await startup()
    s = get_settings()
    invoice_registry = blockchain_client.invoice_registry_contract
    token_contract = blockchain_client.erc1155_contract
    seller = Account.from_key(s.qadmin_private_key)
    buyer = seller
    invoice_id = f'0x{uuid4().hex}'
    debug(invoice_id)
    invoice = invoice_registry.get_invoice(invoice_id)
    debug(invoice)
    assert invoice[0] is False
    token_id = 0
    invoice_amount = 56799
    tx_receipt = invoice_registry.register_invoice(
        seller, invoice_id, buyer.address, token_id, invoice_amount
    )
    # debug(tx_receipt)
    assert tx_receipt['status'] == 1
    invoice = invoice_registry.get_invoice(invoice_id)
    debug(invoice)
    assert (
            invoice[0] is True and
            invoice[2] == seller.address and
            invoice[3] == buyer.address and
            invoice[4] == token_id and
            invoice[5] == invoice_amount and
            invoice[6] == 0 and  # paid amount is 0
            invoice[7] == 0  # state is draft
    )
    tx_receipt = invoice_registry.publish_invoice(
        seller, invoice_id
    )
    # debug(tx_receipt)
    assert tx_receipt['status'] == 1  # invoice accepts payments
    invoice = invoice_registry.get_invoice(invoice_id)
    debug(invoice)
    assert invoice[-1] == 1
    tx_receipt = token_contract.safe_transfer_from(
        buyer, buyer.address, invoice_registry.contract.address,
        token_id, invoice_amount, invoice_id
    )
    debug(tx_receipt)
    assert tx_receipt['status'] == 1
    invoice = invoice_registry.get_invoice(invoice_id)
    debug(invoice)
    assert invoice[-1] == 2  # invoice paid in full


@task
def account_gen(c):
    from eth_account import Account
    account = Account.create()
    print(f'address: {account.address}')
    print(f'key: {account.key.hex()}')


@task
def try_kv(c):
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient

    credential = DefaultAzureCredential()

    # noinspection PyTypeChecker
    secret_client = SecretClient(
        vault_url=os.getenv('chainvoice_key_vault_url'),
        credential=credential)
    secret = secret_client.set_secret("secret-name", "secret-value")

    print(secret.name)
    print(secret.value)
    print(secret.properties.version)


@task
def test_query(c):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_test_query())


async def _test_query():
    await db_client.connect()
    db = db_client.database
    customers = parties.alias('customers')
    query = select([
        customers.c.uid  # .label('customer_uid')
    ]).select_from(
        invoices.join(orders).join(
            customers, orders.c.customer_id == customers.c.id
        )
    ).where(invoices.c.uid == "a731739e-efe6-4f4a-b955-2b9c57160192")
    debug(str(query))
    result = await db.fetch_one(query)
    debug(result)
