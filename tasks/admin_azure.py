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
              f'--admin-enabled true ' \
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


@task
def appservice_create_plan(c):
    command = f'az appservice plan create ' \
              f'--name {c.config.appservice.plan_name} ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--sku {c.config.appservice.sku} ' \
              f'--is-linux ' \
              f'--tags {c.config.tags.owner}'
    run_command(command, c, logger)


@task
def appservice_delete_plan(c):
    command = f'az appservice plan delete ' \
              f'--name {c.config.appservice.plan_name} ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--yes'
    run_command(command, c, logger)


@task
def webapp_create(c):
    command = f'az webapp create ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--plan {c.config.appservice.plan_name} ' \
              f'--name {c.config.appservice.webapp_name} ' \
              f'--deployment-container-image-name ' \
              f'{c.config.image.acr_latest} ' \
              f'--tags {c.config.tags.owner}'
    run_command(command, c, logger)


@task
def webapp_delete(c):
    command = f'az webapp delete ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--name {c.config.appservice.webapp_name}'
    run_command(command, c, logger)


@task
def webapp_restart(c):
    command = f'az webapp restart ' \
              f'--name {c.config.appservice.webapp_name} ' \
              f'--resource-group {c.config.rg.name}'
    run_command(command, c, logger)


@task
def webapp_log_on(c):
    command = f'az webapp log config ' \
              f'--name {c.config.appservice.webapp_name} ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--docker-container-logging filesystem'
    run_command(command, c, logger)


@task
def webapp_log_stream(c):
    command = f'az webapp log tail ' \
              f'--name {c.config.appservice.webapp_name} ' \
              f'--resource-group {c.config.rg.name}'
    run_command(command, c, logger)


@task
def webapp_settings_set(c, settings):
    command = f'az webapp config appsettings set ' \
              f'--name {c.config.appservice.webapp_name} ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--settings {settings}'
    run_command(command, c, logger)


@task
def webapp_identity_assign(c):
    command = f'az webapp identity assign ' \
              f'--name {c.config.appservice.webapp_name} ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--query principalId --output tsv'
    run_command(command, c, logger)


@task
def webapp_perm_cr_pull(c):
    command = f'az role assignment create ' \
              f'--assignee {c.config.appservice.webapp_principal} ' \
              f'--scope /subscriptions/{c.config.subscription}/resourceGroups/' \
              f'{c.config.rg.name}/providers/Microsoft.ContainerRegistry/' \
              f'registries/{c.config.cr.name} ' \
              f'--role "AcrPull"'
    run_command(command, c, logger)


@task
def webapp_container_set(c):
    command = f'az webapp config container set ' \
              f'--name {c.config.appservice.webapp_name} ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--docker-custom-image-name {c.config.image.acr_latest} ' \
              f'--docker-registry-server-url https://{c.config.cr.login_server}'
    run_command(command, c, logger)
