import os
import sys
from pprint import pprint
from invoke import task
from dotenv import load_dotenv

sys.path.append('./chainvoice-client')

from chainvoice_client.client import (
    AuthenticatedClient, Client
)
from chainvoice_client.models import (
    BodyLoginAccessTokenApiLoginAccessTokenPost,
    PartyCreate, PartyGet
)
from chainvoice_client.api.login import (
    login_access_token_api_login_access_token_post
)
from chainvoice_client.api.parties import (
    get_many_api_parties__get,
    create_one_api_parties__post
)
from chainvoice_client.api.users import (
    get_many_api_users__get
)
from chainvoice_client.errors import ApiResponseError


load_dotenv()


@task
def api_parties_get(c):
    client = authenticate()
    pprint(get_many_api_parties__get(client=client))


@task
def api_users_get(c):
    client = authenticate()
    pprint(get_many_api_users__get(client=client))


@task
def api_party_create(c, name):
    client = authenticate()
    party = create_one_api_parties__post(
        client=client,
        json_body=PartyCreate(name=name)
    )
    pprint(party.to_dict())


@task
def create_demo_data(c):
    client = authenticate()
    try:
        parties = get_many_api_parties__get(client=client, limit=100)
        party_names = {p.name for p in parties}
        for i in range(5):
            name = f'Seller {i}'
            if name in party_names:
                continue
            create_one_api_parties__post(
                client=client,
                json_body=PartyCreate(name=name)
            )
        for i in range(25):
            name = f'Buyer {i}'
            if name in party_names:
                continue
            create_one_api_parties__post(
                client=client,
                json_body=PartyCreate(name=name)
            )
        pprint(get_many_api_parties__get(client=client, limit=100))
    except ApiResponseError as error:
        pprint(error.response)


def authenticate():
    client = Client('http://127.0.0.1:8000')
    form_data = BodyLoginAccessTokenApiLoginAccessTokenPost(
        username=os.getenv('chainvoice_su_username'),
        password=os.getenv('chainvoice_su_password'),
        grant_type='password'
    )
    token = login_access_token_api_login_access_token_post(client=client,
                                                           form_data=form_data)
    client = AuthenticatedClient('http://127.0.0.1:8000',
                                 token=token.access_token)
    return client
