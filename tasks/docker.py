from loguru import logger
from invoke import task
from .utils import run_command
from .admin_azure import acr_login


@task
def docker_build(c):
    command = f'docker build -t {c.config.image.name} .'
    run_command(command, c, logger)


@task
def docker_run(c):
    rm_command = f'docker rm -f {c.config.image.name}1'
    run_command(rm_command, c, logger, warn=True)
    command = f'docker run ' \
              f'--name {c.config.image.name}1 ' \
              f'--env-file .env ' \
              f'--env MAX_WORKERS=2 ' \
              f'-p 80:80 {c.config.image.name}'
    run_command(command, c, logger)


@task
def docker_logs(c):
    command = f'docker logs {c.config.image.name}1'
    run_command(command, c, logger)


@task
def docker_tag_acr(c):
    command = f'docker tag {c.config.image.name} {c.config.image.acr_latest}'
    run_command(command, c, logger)


@task
def docker_push_acr(c):
    command = f'docker push {c.config.image.acr_latest}'
    run_command(command, c, logger)


@task(pre=[
    docker_build, docker_tag_acr, acr_login, docker_push_acr
])
def docker_build_push(c):
    pass
