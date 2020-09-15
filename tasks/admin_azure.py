from loguru import logger
import os
from invoke import task
from dotenv import load_dotenv
from .utils import run_command
from app.config import get_settings


load_dotenv()


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
def chainvoice_settings_set(c):
    settings = get_settings().dict()
    included_vars = [
        'secret_key',
        'access_token_expire_minutes',
        'database_url',
        'su_username',
        'su_password',
        'su_email',
        'su_name'
    ]
    var_values = ' '.join(f'chainvoice_{name}="{settings[name]}"'
                          for name in included_vars)
    webapp_settings_set(c, var_values)


@task
def webapp_settings_list(c):
    command = f'az webapp config appsettings list ' \
              f'--name {c.config.appservice.webapp_name} ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--output table'
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


@task
def webapp_https_only(c):
    command = f'az webapp update ' \
              f'--name {c.config.appservice.webapp_name} ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--https-only true'
    run_command(command, c, logger)


@task
def db_up(c):
    """
    Create a resource group, if it doesn't already exist.
    Create a Postgres server.
    Create a default administrator account with a unique user name and password.
    Create a database.
    Enable access from your local IP address.
    Enable access from Azure services.
    Create a database user with access to the database.
    :param c:
    :return:
    """
    command = f'az postgres up ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--location {c.config.rg.location} ' \
              f'--sku-name {c.config.db.sku} ' \
              f'--server-name {c.config.db.server_name} ' \
              f'--database-name {c.config.db.db_name} ' \
              f'--admin-user {c.config.db.admin_username} ' \
              f'--admin-password {os.getenv("database_admin_password")} ' \
              f'--ssl-enforcement Enabled'
    run_command(command, c, logger)


@task
def blockchain_member_create(c):
    member_password = os.getenv("chainvoice_consortium_member_password")
    account_password = os.getenv(
        "chainvoice_consortium_management_account_password"
    )
    command = f'az blockchain member create ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--name {c.config.blockchain.member_name} ' \
              f'--location {c.config.rg.location} ' \
              f'--password {member_password} ' \
              f'--protocol {c.config.blockchain.protocol} ' \
              f'--consortium {c.config.blockchain.consortium} ' \
              f'--consortium-management-account-password {account_password} ' \
              f'--sku {c.config.blockchain.sku} ' \
              f'--tags {c.config.tags.owner}'
    run_command(command, c, logger)


@task
def keyvault_create(c):
    command = f'az keyvault create ' \
              f'--name {c.config.kv.name} ' \
              f'--resource-group {c.config.rg.name} ' \
              f'--location {c.config.rg.location} ' \
              f'--tags {c.config.tags.owner}'
    run_command(command, c, logger)

