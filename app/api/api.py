from fastapi import APIRouter
from . import (notes, party_api, user_api, login_api)


api_router = APIRouter()
# api_router.include_router(notes.router, prefix='/notes', tags=['notes'])
api_router.include_router(
    party_api.router, prefix='/parties', tags=['parties']
)
api_router.include_router(
    user_api.router, prefix='/users', tags=['users']
)
api_router.include_router(
    login_api.router, prefix='/login', tags=['login']
)
