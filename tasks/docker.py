import logging
from invoke import task
from .utils import run_command


logger = logging.getLogger(__name__)


@task
def docker_build(c):
    command = f'docker build -t {c.config.image.name} .'
    run_command(command, c, logger)


@task
def docker_run(c):
    command = f'docker run -d ' \
              f'--name {c.config.image.name}1 ' \
              f'-p 80:80 {c.config.image.name}'
    run_command(command, c, logger)


@task
def docker_tag_acr(c):
    command = f'docker tag {c.config.image.name} {c.config.image.acr_latest}'
    run_command(command, c, logger)


@task
def docker_push_acr(c):
    command = f'docker push {c.config.image.acr_latest}'
    run_command(command, c, logger)

