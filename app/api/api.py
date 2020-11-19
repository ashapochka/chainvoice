from fastapi import APIRouter

from . import (
    party_api, user_api, login_api,
    catalog_api, catalog_item_api,
    order_api, order_item_api,
    invoice_api, payment_api,
    blockchain_contract_api,
    ledger_state_api
)

apis = [
    (login_api, 'login'),
    (blockchain_contract_api, 'blockchain-contracts'),
    (user_api, 'users'),
    (party_api, 'parties'),
    (catalog_api, 'catalogs'),
    (catalog_item_api, 'catalog-items'),
    (order_api, 'orders'),
    (order_item_api, 'order-items'),
    (invoice_api, 'invoices'),
    (payment_api, 'payments'),
    (ledger_state_api, 'ledger')
]


api_router = APIRouter()

for api in apis:
    api_router.include_router(
        api[0].router, prefix=f'/{api[1]}', tags=[api[1]]
    )
