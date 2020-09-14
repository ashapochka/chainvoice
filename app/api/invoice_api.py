from typing import List
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.api_model import APIMessage

from ..services import invoice_service
from ..schemas import (
    InvoiceCreate, InvoiceUpdate, InvoiceGet,
)
from .base_api import BaseAPI

router = InferringRouter()


# noinspection PyTypeChecker
@cbv(router)
class InvoiceAPI(BaseAPI):
    service = invoice_service

    @router.get('/')
    async def get_many(
            self, offset: int = 0, limit: int = 20,
            order_uid: str = None
    ) -> List[InvoiceGet]:
        return await self._get_many(
            limit, offset, order_uid=order_uid
        )

    @router.get("/{uid}/")
    async def get_one(
            self, uid: str
    ) -> InvoiceGet:
        return await self._get_one(uid)

    @router.post("/")
    async def create_one(
            self, obj: InvoiceCreate
    ) -> InvoiceGet:
        return await self._create_one(obj)

    @router.put("/{uid}/")
    async def update_one(
            self, uid: str, obj: InvoiceUpdate
    ) -> InvoiceGet:
        return await self._update_one(obj, uid)

    @router.delete("/{uid}/")
    async def delete_one(
            self, uid: str
    ) -> APIMessage:
        return await self._delete_one(uid)
