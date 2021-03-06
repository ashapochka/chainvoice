from typing import List
from uuid import UUID

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.api_model import APIMessage

from ..services import PaymentService
from ..schemas import (
    PaymentCreate, PaymentUpdate, PaymentGet,
)
from .base_api import BaseAPI

router = InferringRouter()


# noinspection PyTypeChecker
@cbv(router)
class PaymentAPI(BaseAPI):
    service: PaymentService = Depends()

    @router.get('/')
    async def get_many(
            self, offset: int = 0, limit: int = 20,
            invoice_uid: UUID = None
    ) -> List[PaymentGet]:
        return await self._get_many(
            limit, offset, invoice_uid=invoice_uid
        )

    @router.get("/{uid}/")
    async def get_one(
            self, uid: UUID
    ) -> PaymentGet:
        return await self._get_one(uid)

    @router.post("/")
    async def create_one(
            self, obj: PaymentCreate
    ) -> PaymentGet:
        return await self._create_one(obj)

    @router.put("/{uid}/")
    async def update_one(
            self, uid: UUID, obj: PaymentUpdate
    ) -> PaymentGet:
        return await self._update_one(obj, uid)

    @router.delete("/{uid}/")
    async def delete_one(
            self, uid: UUID
    ) -> APIMessage:
        return await self._delete_one(uid)
