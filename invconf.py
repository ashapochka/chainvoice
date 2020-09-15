# cross resource
subscription = '5a1f3d2e-15e3-4ace-a76c-73b7c1df42ca'
company_name = 'softserveinc'
tenant_prefix = f'{company_name}-demo'
app_name = "chainvoice"

tags = {
    'owner': "owner=ashapoch",
}


# resource group
rg = {
    'name': f"{app_name}RG",
    'location': "westeurope"
}

# container registry
cr = {
    'name': f'{app_name}CR',
    'sku': 'Basic',
    'login_server': f"{app_name}cr.azurecr.io"
}

# docker
image = {
    'name': app_name,
    'acr_name': f"{cr['login_server']}/{app_name}",
    'acr_latest': f"{cr['login_server']}/{app_name}:latest"
}

# app service
# webapp_principal is dynamic, from task webapp_identity_assign
appservice = {
    'plan_name': f"{app_name}-plan",
    'sku': 'B1',
    'webapp_name': f'{tenant_prefix}-{app_name}',
    'webapp_fqdn': f'{tenant_prefix}-{app_name}.azurewebsites.net',
    'webapp_principal': '614a96a5-2ea4-4675-91c7-dc1552196cc9'
}

# postgresql database
db = {
    'sku': 'B_Gen5_1',
    'server_name': f'{tenant_prefix}-{app_name}',
    'db_name': f'{app_name}',
    'admin_username': f'{app_name}_admin' # don't use 'admin' it's reserved
}

# blockchain service
# The blockchain member and consortium names
# can contain only lowercase letters and numbers.
# The first character must be a letter.
# The value must be between 2 and 20 characters long.
blockchain = {
    'member_name': f'ssdemo{app_name}',
    'sku': 'Basic',
    'protocol': 'Quorum',
    'consortium': f'ssdemo{app_name}ctium',
}

# key vault
kv = {
    'name': f'ssdemo-{app_name}'
}
