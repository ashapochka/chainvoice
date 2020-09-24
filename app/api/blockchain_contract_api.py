from typing import List
from uuid import UUID

from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.api_model import APIMessage

from ..services import blockchain_contract_service
from ..schemas import (
    BlockchainContractCreate, BlockchainContractUpdate, BlockchainContractGet,
)
from .base_api import BaseAPI

router = InferringRouter()


# noinspection PyTypeChecker
@cbv(router)
class BlockchainContractAPI(BaseAPI):
    service = blockchain_contract_service

    @router.get('/')
    async def get_many(
            self, offset: int = 0, limit: int = 20,
            name: str = None
    ) -> List[BlockchainContractGet]:
        return await self._get_many(
            limit, offset, name=name
        )

    @router.get("/{uid}/")
    async def get_one(
            self, uid: UUID
    ) -> BlockchainContractGet:
        return await self._get_one(uid)

    @router.post("/")
    async def create_one(
            self, obj: BlockchainContractCreate
    ) -> BlockchainContractGet:
        return await self._create_one(obj)

    @router.put("/{uid}/")
    async def update_one(
            self, uid: UUID, obj: BlockchainContractUpdate
    ) -> BlockchainContractGet:
        return await self._update_one(obj, uid)

    @router.delete("/{uid}/")
    async def delete_one(
            self, uid: UUID
    ) -> APIMessage:
        return await self._delete_one(uid)
