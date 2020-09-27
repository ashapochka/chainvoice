import random
from typing import Dict, Type, List

import httpx
from devtools import debug
from httpx import Response
from invoke import task
from pydantic import BaseModel

from app.config import get_settings
from app.schemas import (
    Token, PartyGet, PartyCreate, CatalogCreate, CatalogGet,
    CatalogItemCreate, CatalogItemGet, UserGet
)

from .fixtures import RootPartiesFixture


class LoginFormData(BaseModel):
    username: str
    password: str
    grant_type: str = 'password'


def check_response(response: Response):
    if response.is_error:
        debug(response.json())
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


def authorized_client() -> httpx.Client:
    api_client = ApiClient()
    api_client.authenticate()
    return api_client.new_client()


def create_party(client, new_party_name):
    return create_one(
        client, 'parties', PartyCreate(name=new_party_name), PartyGet
    )


def create_one(
        client, obj_path, obj: BaseModel, obj_get_class: Type[BaseModel]
):
    obj_json = obj.json(exclude_unset=True)
    debug(obj_json)
    response = client.post(f'/api/{obj_path}/', data=obj_json)
    check_response(response)
    new_obj = obj_get_class.parse_obj(response.json())
    return new_obj


def get_many(
        client: httpx.Client,
        obj_path: str, obj_class: Type[BaseModel],
        offset: int = 0,
        limit: int = 20,
        **kwargs
) -> List:
    params = {
        'offset': offset if offset >= 0 else 0,
        'limit': limit if limit >= 0 else 0,
        **kwargs
    }
    response = client.get(f'/api/{obj_path}/', params=params)
    check_response(response)
    objs = [obj_class.parse_obj(obj) for obj in response.json()]
    return objs


@task
def api_parties_get(c):
    with authorized_client() as client:
        debug(get_many(client, 'parties', PartyGet))


@task
def api_users_get(c):
    with authorized_client() as client:
        debug(get_many(client, 'users', UserGet))


@task
def api_party_create(c, name):
    with authorized_client() as client:
        party = create_party(client, name)
        debug(party)


@task
def create_random_order(c, max_attempts=10):
    with authorized_client() as client:
        parties = get_many(client, 'parties', PartyGet, limit=100)
        # select a seller
        attempts = 0
        while attempts < max_attempts:
            seller = random.choice(parties)
            catalogs = get_many(
                client, 'catalogs', CatalogGet, seller_uid=seller.uid
            )
            if not len(catalogs) or not seller.blockchain_account_address:
                attempts += 1  # party cannot be a seller
            else:
                break  # seller found
        else:
            debug(f'seller not found after {attempts} attempts, exiting.')
            return
        # select a buyer
        attempts = 0
        while attempts < max_attempts:
            buyer = random.choice(parties)
            if buyer is seller or not buyer.blockchain_account_address:
                attempts += 1  # party cannot be a buyer
            else:
                break  # buyer found
        else:
            debug(f'buyer not found after {attempts} attempts, exiting.')
            return
        debug(seller)
        debug(buyer)
        # buyer selects seller's catalogs to buy items from
        n_catalogs_to_select = random.randint(1, len(catalogs))
        selected_catalogs = []
        attempts = 0
        while attempts < max_attempts * n_catalogs_to_select:
            catalog = random.choice(catalogs)
            if catalog in selected_catalogs:
                attempts += 1
            else:
                selected_catalogs.append(catalog)
                if len(selected_catalogs) == n_catalogs_to_select:
                    break  # buyer selected catalogs
        else:
            debug(f'failed to select {n_catalogs_to_select} catalogs, exiting.')
            return
        debug(selected_catalogs)


# noinspection PyTypeChecker
@task
def create_demo_data(c):
    root = RootPartiesFixture.parse_file(
        './fixtures/parties-catalogs.json'
    )
    with authorized_client() as client:
        parties = get_many(client, 'parties', PartyGet, limit=100)
        party_names = {p.name for p in parties}
        for p in root.parties:
            new_party_name = p.name
            if new_party_name in party_names:
                continue
            new_party: PartyGet = create_party(client, new_party_name)
            debug(new_party=new_party)
            if not p.catalogs:
                continue
            for c in p.catalogs:
                new_catalog: CatalogGet = create_one(
                    client, 'catalogs', CatalogCreate(
                        name=c.name,
                        seller_uid=new_party.uid
                    ), CatalogGet
                )
                debug(new_catalog=new_catalog)
                for item in c.catalog_items:
                    new_item = create_one(
                        client, 'catalog-items', CatalogItemCreate(
                            name=item.name,
                            price=item.price,
                            catalog_uid=new_catalog.uid
                        ), CatalogItemGet
                    )
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
            catalog_name = f"{party_name}'s Catalog {j + 1}"
            for k in range(random.randint(10, 30)):
                item_type = random.choice(
                    3 * ('Product',) + 5 * ('Part',) + 2 * ('Service',)
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
                    name=f"{item_type} {k + 1} from {catalog_name}",
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
