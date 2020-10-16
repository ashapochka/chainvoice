from typing import List
from uuid import UUID

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.api_model import APIMessage

from ..services import OrderService
from ..schemas import (
    OrderCreate, OrderUpdate, OrderGet,
)
from .base_api import BaseAPI

router = InferringRouter()


# noinspection PyTypeChecker
@cbv(router)
class OrderAPI(BaseAPI):
    service: OrderService = Depends()

    @router.get('/')
    async def get_many(
            self,
            offset: int = 0, limit: int = 20,
            ref_id: str = None,
            seller_uid: UUID = None,
            customer_uid: UUID = None
    ) -> List[OrderGet]:
        return await self._get_many(
            limit, offset,
            ref_id=ref_id,
            seller_uid=seller_uid,
            customer_uid=customer_uid
        )

    @router.get("/{uid}/")
    async def get_one(
            self, uid: UUID
    ) -> OrderGet:
        return await self._get_one(uid)

    @router.post("/")
    async def create_one(
            self, obj: OrderCreate
    ) -> OrderGet:
        return await self._create_one(obj)

    @router.put("/{uid}/")
    async def update_one(
            self, uid: UUID, obj: OrderUpdate
    ) -> OrderGet:
        return await self._update_one(obj, uid)

    @router.delete("/{uid}/")
    async def delete_one(
            self, uid: UUID
    ) -> APIMessage:
        return await self._delete_one(uid)
