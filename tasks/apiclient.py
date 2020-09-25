from typing import Dict

import httpx
from devtools import debug
from httpx import Response
from invoke import task
from pydantic import BaseModel

from app.config import get_settings
from app.schemas import (
    Token, PartyGet, PartyCreate, CatalogCreate, CatalogGet,
    CatalogItemCreate, CatalogItemGet
)

from .fixtures import RootPartiesFixture


class LoginFormData(BaseModel):
    username: str
    password: str
    grant_type: str = 'password'


def check_response(response: Response):
    if response.is_error:
        debug(response)
        response.raise_for_status()


class ApiClient:
    base_url: str
    auth_headers: Dict[str, str]
    timeout: int

    def __init__(
            self, base_url: str = 'http://127.0.0.1:8000', timeout: int = 30
    ):
        self.base_url = base_url
        self.timeout = timeout

    def authenticate(self):
        s = get_settings()
        form_data = LoginFormData(
            username=s.su_username,
            password=s.su_password,
        )
        with self.new_client(authenticated=False) as client:
            response = client.post(
                url='/api/login/access-token', data=form_data.dict()
            )
            check_response(response)
            token = Token.parse_obj(response.json())
            self.auth_headers = {
                "Authorization": f"Bearer {token.access_token}"
            }

    def new_client(self, authenticated: bool = True):
        return httpx.Client(
            base_url=self.base_url, timeout=self.timeout,
            headers=self.auth_headers if authenticated else {}
        )


# @task
# def api_parties_get(c):
#     client = authenticate()
#     debug(get_many_api_parties__get(client=client))
#
#
# @task
# def api_users_get(c):
#     client = authenticate()
#     debug(get_many_api_users__get(client=client))
#
#
# @task
# def api_party_create(c, name):
#     client = authenticate()
#     party = create_one_api_parties__post(
#         client=client,
#         json_body=PartyCreate(name=name)
#     )
#     debug(party.to_dict())


@task
def create_demo_data(c):
    root = RootPartiesFixture.parse_file(
        './fixtures/parties-catalogs.json'
    )

    api_client = ApiClient()
    api_client.authenticate()

    with api_client.new_client() as client:
        response = client.get('/api/parties/', params={'limit': 100})
        check_response(response)
        parties = [PartyGet.parse_obj(obj) for obj in response.json()]
        party_names = {p.name for p in parties}
        for p in root.parties:
            if p.name in party_names:
                continue
            response = client.post(
                '/api/parties/', data=PartyCreate(name=p.name).json()
            )
            check_response(response)
            new_party = PartyGet.parse_obj(response.json())
            debug(new_party=new_party)
            if not p.catalogs:
                continue
            for c in p.catalogs:
                response = client.post(
                    '/api/catalogs/',
                    data=CatalogCreate(
                        name=c.name,
                        seller_uid=new_party.uid
                    ).json()
                )
                check_response(response)
                new_catalog = CatalogGet.parse_obj(response.json())
                debug(new_catalog=new_catalog)
                for item in c.catalog_items:
                    response = client.post(
                        '/api/catalog-items/',
                        data=CatalogItemCreate(
                            name=item.name,
                            price=item.price,
                            catalog_uid=new_catalog.uid
                        ).json()
                    )
                    check_response(response)
                    new_item = CatalogItemGet.parse_obj(response.json())
                    debug(new_item=new_item)


@task
def fixture_gen(c):
    from .fixtures import (
        RootPartiesFixture, PartyFixture, CatalogFixture, CatalogItemFixture
    )
    import random
    from faker import Faker
    fake = Faker()
    seed = 43
    random.seed(seed)
    party_number = 10
    parties = []
    for i in range(party_number):
        party_name = fake.company()
        catalogs = []
        for j in range(random.randint(1, 3)):
            items = []
            catalog_name = f"{party_name}'s Catalog {j+1}"
            for k in range(random.randint(10, 30)):
                item_type = random.choice(
                    3*('Product',) + 5*('Part',) + 2*('Service',)
                )
                if item_type == 'Product':
                    low, high = 50, 1000
                elif item_type == 'Part':
                    low, high = 1, 200
                else:
                    low, high = 100, 500
                item_price = random.uniform(low, high)
                if item_type == 'Service':
                    round_digits = 0
                else:
                    round_digits = 2
                item_price = round(item_price, round_digits)
                items.append(CatalogItemFixture(
                    name=f"{item_type} {k+1} from {catalog_name}",
                    price=item_price
                ))
            catalogs.append(CatalogFixture(
                name=catalog_name, catalog_items=items
            ))
        party = PartyFixture(name=party_name)
        if catalogs:
            party.catalogs = catalogs
        parties.append(party)
    with open('./fixtures/parties-catalogs.json', 'w') as f:
        f.write(RootPartiesFixture(parties=parties).json(
            exclude_unset=True, indent=4
        ))


