from typing import List
from uuid import UUID

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.api_model import APIMessage

from ..services import OrderItemService
from ..schemas import (
    OrderItemCreate, OrderItemUpdate, OrderItemGet,
)
from .base_api import BaseAPI

router = InferringRouter()


# noinspection PyTypeChecker
@cbv(router)
class OrderItemAPI(BaseAPI):
    service: OrderItemService = Depends()

    @router.get('/')
    async def get_many(
            self, offset: int = 0, limit: int = 20,
            order_uid: UUID = None
    ) -> List[OrderItemGet]:
        return await self._get_many(
            limit, offset, order_uid=order_uid
        )

    @router.get("/{uid}/")
    async def get_one(
            self, uid: UUID
    ) -> OrderItemGet:
        return await self._get_one(uid)

    @router.post("/")
    async def create_one(
            self, obj: OrderItemCreate
    ) -> OrderItemGet:
        return await self._create_one(obj)

    @router.put("/{uid}/")
    async def update_one(
            self, uid: UUID, obj: OrderItemUpdate
    ) -> OrderItemGet:
        return await self._update_one(obj, uid)

    @router.delete("/{uid}/")
    async def delete_one(
            self, uid: UUID
    ) -> APIMessage:
        return await self._delete_one(uid)
