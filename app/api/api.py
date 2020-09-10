from fastapi import APIRouter
from . import (notes, party_api)


api_router = APIRouter()
# api_router.include_router(notes.router, prefix='/notes', tags=['notes'])
api_router.include_router(
    party_api.router, prefix='/parties', tags=['parties']
)
