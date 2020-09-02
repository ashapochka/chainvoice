import logging
from invoke import task
from .utils import run_command


logger = logging.getLogger(__name__)


@task
def rg_create(c):
    command = f'az group create ' \
              f'--name {c.config.rg.name} ' \
              f'--location {c.config.rg.location} ' \
              f'--tags {c.config.tags.owner}'
    run_command(command, c, logger)


@task
def rg_delete(c):
    command = f"az group delete --yes " \
              f"--name {c.config.rg.name} "
    run_command(command, c, logger)


@task
def acr_create(c):
    command = f'az acr create ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--name {c.config.cr.name} ' \
              f'--sku {c.config.cr.sku} ' \
              f'--tags {c.config.tags.owner}'
    run_command(command, c, logger)


@task
def acr_login(c):
    command = f'az acr login ' \
              f'--name {c.config.cr.name.lower()}'
    run_command(command, c, logger)


@task
def acr_list(c):
    command = f'az acr repository list ' \
              f'--name {c.config.cr.name} ' \
              f'--output table'
    run_command(command, c, logger)


@task
def acr_tags(c):
    command = f'az acr repository show-tags ' \
              f'--name {c.config.cr.name} ' \
              f'--repository {c.config.image.name} ' \
              f'--output table'
    run_command(command, c, logger)
