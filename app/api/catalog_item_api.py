from typing import List
from uuid import UUID

from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.api_model import APIMessage

from ..services import catalog_item_service
from ..schemas import (
    CatalogItemCreate, CatalogItemUpdate, CatalogItemGet,
)
from .base_api import BaseAPI

router = InferringRouter()


# noinspection PyTypeChecker
@cbv(router)
class CatalogItemAPI(BaseAPI):
    service = catalog_item_service

    @router.get('/')
    async def get_many(
            self, offset: int = 0, limit: int = 20,
            catalog_uid: UUID = None
    ) -> List[CatalogItemGet]:
        return await self._get_many(
            limit, offset, catalog_uid=catalog_uid
        )

    @router.get("/{uid}/")
    async def get_one(
            self, uid: UUID
    ) -> CatalogItemGet:
        return await self._get_one(uid)

    @router.post("/")
    async def create_one(
            self, obj: CatalogItemCreate
    ) -> CatalogItemGet:
        return await self._create_one(obj)

    @router.put("/{uid}/")
    async def update_one(
            self, uid: UUID, obj: CatalogItemUpdate
    ) -> CatalogItemGet:
        return await self._update_one(obj, uid)

    @router.delete("/{uid}/")
    async def delete_one(
            self, uid: UUID
    ) -> APIMessage:
        return await self._delete_one(uid)
