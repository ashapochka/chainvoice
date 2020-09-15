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
