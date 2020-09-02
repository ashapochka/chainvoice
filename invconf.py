# cross resource
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
