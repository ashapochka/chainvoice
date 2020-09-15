import os
import string
import secrets
from invoke import task
from loguru import logger

from .utils import run_command


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

    url = os.getenv("chainvoice_qnode_url")
    access_key = os.getenv("chainvoice_qnode_key")
    w3 = Web3(Web3.HTTPProvider(f'{url}/{access_key}'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print(f'connected: {w3.isConnected()}')
    account = w3.eth.account.create()
    print(f'address: {account.address}, key: {account.key}')
    same_account = w3.eth.account.from_key(account.key)
    print(f'address: {same_account.address}, key: {same_account.key}')
