from fastapi import APIRouter
from . import (
    notes, party_api, user_api,
    login_api, catalog_api, order_api
)


api_router = APIRouter()
# api_router.include_router(notes.router, prefix='/notes', tags=['notes'])
api_router.include_router(
    login_api.router, prefix='/login', tags=['login']
)
api_router.include_router(
    user_api.router, prefix='/users', tags=['users']
)
api_router.include_router(
    party_api.router, prefix='/parties', tags=['parties']
)
api_router.include_router(
    catalog_api.router, prefix='/catalogs', tags=['catalogs']
)
api_router.include_router(
    order_api.router, prefix='/orders', tags=['orders']
)
