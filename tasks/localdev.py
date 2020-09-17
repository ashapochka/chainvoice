import os
import string
import secrets
from invoke import task
from loguru import logger

from .utils import run_command


# https://docs.microsoft.com/en-us/azure/developer/python/configure-local-development-environment?tabs=bash


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


@task
def try_quorum(c):
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    import json

    url = os.getenv("chainvoice_qnode_url")
    access_key = os.getenv("chainvoice_qnode_key")
    w3 = Web3(Web3.HTTPProvider(f'{url}/{access_key}'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print(f'connected: {w3.isConnected()}')
    with open('build/contracts/Box.json') as f:
        compiled_contract = json.load(f)
        box_abi = compiled_contract['abi']
    contract_address = os.getenv('chainvoice_contract_address_box')
    account_address = os.getenv('chainvoice_qadmin_address')
    w3.eth.defaultAccount = account_address
    account_key = os.getenv('chainvoice_qadmin_private_key')
    box = w3.eth.contract(
        address=contract_address,
        abi=box_abi
    )
    contract_call = box.functions.store(11)
    # print(f'estimated gas: {contract_call.estimateGas()}')
    # return
    nonce = w3.eth.getTransactionCount(account_address)
    txn = contract_call.buildTransaction({
        'nonce': nonce,
        'gas': 100000
    })
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=account_key)
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f'txn_hash: {txn_hash}')
    txn_receipt = w3.eth.waitForTransactionReceipt(txn_hash)
    print(f'txn_receipt: {txn_receipt}')


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
