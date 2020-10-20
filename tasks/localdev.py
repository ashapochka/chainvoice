import asyncio
import json
import os
import string
import secrets
from uuid import uuid4

from devtools import debug
from eth_account import Account
from web3 import Web3
from web3.middleware import geth_poa_middleware
from invoke import task
from loguru import logger

from app.config import get_settings
from app.main import startup
from app.blockchain import blockchain_client
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


@task
def token_transfer(c):
    w3 = create_w3()
    with open('build/contracts/ChainvoiceERC1155.json') as f:
        compiled_contract = json.load(f)
        contract_abi = compiled_contract['abi']
        assert contract_abi
    contract_address = os.getenv('chainvoice_erc1155_contract_address')
    erc1155 = ERC1155Contract(w3, contract_address, contract_abi)
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
    # w3 = create_w3_local()
    w3 = create_w3()
    with open('build/contracts/InvoiceRegistry.json') as f:
        compiled_contract = json.load(f)
        contract_abi = compiled_contract['abi']
        assert contract_abi
    # contract_address = '0x59d3631c86BbE35EF041872d502F218A39FBa150'
    contract_address = os.getenv('chainvoice_invoice_registry_contract_address')
    contract = InvoiceRegistryContract(w3, contract_address, contract_abi)
    # owner_key =
    # '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'
    owner_key = os.getenv('chainvoice_qadmin_private_key')
    owner = Account.from_key(owner_key)
    debug(w3.eth.getBalance(owner.address))
    # other_address = '0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0'
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
