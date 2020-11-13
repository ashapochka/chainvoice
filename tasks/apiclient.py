import random
import time
from collections import Counter
from json import JSONDecodeError
from typing import Dict, Type, List, TypeVar, SupportsAbs

import httpx
from devtools import debug
from fastapi_utils.api_model import APIMessage
from httpx import Response
from invoke import task, Exit
from pydantic import BaseModel

from app.config import get_settings
from app.schemas import (
    Token, PartyGet, PartyCreate, CatalogCreate, CatalogGet,
    CatalogItemCreate, CatalogItemGet, UserGet, OrderCreate, OrderItemCreate,
    OrderGet, OrderItemGet, InvoiceGet, InvoiceCreate, PaymentGet,
    PaymentCreate, OrderAmount, InvoiceBlockchainGet, PartyTokenBalance,
    PartyTokenTransfer, PartyTokenTransferReceipt
)
from app.services.utils import money_to_token

from .fixtures import RootPartiesFixture


class LoginFormData(BaseModel):
    username: str
    password: str
    grant_type: str = 'password'


def check_response(response: Response):
    if response.is_error:
        try:
            debug(response.json())
        except JSONDecodeError:
            pass
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
                url='/api/login/access-token/', data=form_data.dict()
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
        client, obj_path, obj, obj_get_class
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
        'offset': max(offset, 0),
        'limit': max(limit, 0),
        **{k: v for k, v in kwargs.items() if v is not None}
    }
    response = client.get(f'/api/{obj_path}/', params=params)
    check_response(response)
    objs = [obj_class.parse_obj(obj) for obj in response.json()]
    return objs


def get_one(
        client: httpx.Client,
        obj_path: str, obj_class,
        obj_uid: str, path_tail: str = None
):
    path = f'api/{obj_path}/{obj_uid}'
    if path_tail:
        path = f'{path}/{path_tail}'
    response = client.get(f'/{path}/')
    check_response(response)
    obj = obj_class.parse_obj(response.json())
    return obj


def get_order_total_amount(
        client: httpx.Client,
        order_uid: str
) -> OrderAmount:
    return get_one(
        client, 'orders', OrderAmount, order_uid, path_tail='total-amount'
    )


def get_invoice_blockchain_state(
        client: httpx.Client,
        invoice_uid: str
) -> InvoiceBlockchainGet:
    return get_one(
        client, 'invoices', InvoiceBlockchainGet,
        invoice_uid, path_tail='blockchain-state'
    )


@task
def api_parties_get(c, name=None):
    with authorized_client() as client:
        debug(get_many(client, 'parties', PartyGet, name=name))


@task
def api_users_get(c):
    with authorized_client() as client:
        debug(get_many(client, 'users', UserGet))


@task
def api_orders_get(c, ref_id=None, seller_id=None, customer_id=None):
    filters = dict(ref_id=ref_id, seller_id=seller_id, customer_id=customer_id)
    with authorized_client() as client:
        debug(get_many(client, 'orders', OrderGet, **filters))


@task
def api_party_create(c, name):
    with authorized_client() as client:
        party = create_party(client, name)
        debug(party)


# noinspection PyTypeChecker
@task
def api_invoice_create(c, order_uid):
    with authorized_client() as client:
        _create_invoice(client, order_uid)


def _publish_invoice(client, invoice_uid) -> APIMessage:
    response = client.post(f'/api/invoices/{invoice_uid}/publish/')
    check_response(response)
    new_obj = APIMessage.parse_obj(response.json())
    debug(new_obj)
    return new_obj


# noinspection PyTypeChecker
def _create_payment(client, invoice_uid, amount):
    payment: PaymentGet = create_one(
        client, 'payments', PaymentCreate(
            invoice_uid=invoice_uid,
            amount=amount
        ), PaymentGet
    )
    debug(payment)
    return payment


def _check_invoice_blockchain_state(
        client, invoice_uid: str, expected_state: str = None
):
    invoice = get_invoice_blockchain_state(client, invoice_uid)
    debug(invoice)
    if expected_state:
        assert invoice.state == expected_state


def _get_party_token_balance(
        client, party_uid, token_id=0
) -> PartyTokenBalance:
    return get_one(
        client, 'parties', PartyTokenBalance,
        party_uid, path_tail=f'token-balance/{token_id}'
    )


def _transfer_tokens(
        client, from_party_uid, to_party_uid, token_amount, token_id=0
) -> PartyTokenTransferReceipt:
    return create_one(
        client, f'parties/{from_party_uid}/token-transfer',
        PartyTokenTransfer(
            token_id=token_id,
            token_amount=token_amount,
            to_uid=to_party_uid,
            data='0x0'
        ),
        PartyTokenTransferReceipt
    )


def _ensure_token_balance(client, party_uid, balance, token_id=0):
    current_balance = _get_party_token_balance(
        client, party_uid, token_id=token_id
    )
    debug(current_balance)
    new_balance = int(balance)
    if current_balance.token_amount < new_balance:
        amount_to_transfer = new_balance - current_balance.token_amount
        qadmin = _get_admin_party(client)
        receipt = _transfer_tokens(
            client, qadmin.uid, party_uid,
            amount_to_transfer, token_id=token_id
        )
        debug(receipt)
    else:
        debug('balance is already good!')


def _get_admin_party(client) -> PartyGet:
    s = get_settings()
    admin_name = s.qadmin_name
    parties = get_many(client, 'parties', PartyGet, name=admin_name)
    assert len(parties)
    return parties[0]


@task
def party_ensure_balance(c, party_uid, balance):
    with authorized_client() as client:
        _ensure_token_balance(client, party_uid, balance)


@task
def demo_order_invoice_flow(c):
    with authorized_client() as client:
        order = _create_random_order(client)
        order_amount = get_order_total_amount(client, order.uid)
        invoice = _create_invoice(client, order.uid)
        _check_invoice_blockchain_state(client, invoice.uid, '0')  # DRAFT
        _publish_invoice(client, invoice.uid)
        _check_invoice_blockchain_state(client, invoice.uid, '1')  # UNPAID
        _ensure_token_balance(
            client, order.customer_uid, money_to_token(order_amount.amount)
        )
        _create_payment(client, invoice.uid, order_amount.amount)
        _check_invoice_blockchain_state(client, invoice.uid, '2')  # PAID


# noinspection PyTypeChecker
def _create_invoice(client, order_uid) -> InvoiceGet:
    invoice: InvoiceGet = create_one(
        client, 'invoices', InvoiceCreate(
            order_uid=order_uid,
        ), InvoiceGet
    )
    debug(invoice)
    return invoice


# noinspection PyTypeChecker
@task
def create_random_order(c, max_attempts=10):
    with authorized_client() as client:
        _create_random_order(client, max_attempts=max_attempts)


# noinspection PyTypeChecker
def _create_random_order(client, max_attempts=10) -> OrderGet:
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
        raise Exit(f'seller not found after {attempts} attempts, exiting.')
    # select a buyer
    attempts = 0
    while attempts < max_attempts:
        buyer = random.choice(parties)
        if buyer is seller or not buyer.blockchain_account_address:
            attempts += 1  # party cannot be a buyer
        else:
            break  # buyer found
    else:
        raise Exit(f'buyer not found after {attempts} attempts, exiting.')
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
        raise Exit(
            f'failed to select {n_catalogs_to_select} catalogs, exiting.'
        )
    debug(selected_catalogs)
    selected_items = []
    for catalog in selected_catalogs:
        catalog_items = get_many(
            client, 'catalog-items', CatalogItemGet, catalog_uid=catalog.uid
        )
        n_items = random.randint(1, min(5, len(catalog_items)))
        selected_items.extend(random.choices(catalog_items, k=n_items))
    debug(selected_items)
    item_map = {item.uid: item for item in selected_items}
    item_quantities = dict(Counter(item.uid for item in selected_items))
    order: OrderGet = create_one(
        client, 'orders', OrderCreate(
            seller_uid=seller.uid,
            customer_uid=buyer.uid,
            ref_id=f'PO-{int(time.time())}'
        ), OrderGet
    )
    debug(order)
    for item_uid, item in item_map.items():
        order_item: OrderItemGet = create_one(
            client, 'order-items', OrderItemCreate(
                order_uid=order.uid,
                catalog_item_uid=item_uid,
                quantity=item_quantities[item_uid],
                base_price=item.price
            ), OrderItemGet
        )
        debug(order_item)
    return order


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
