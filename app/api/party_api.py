from typing import List
from uuid import UUID

from fastapi import (Depends, Path)
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.api_model import APIMessage

from ..contracts import ERC1155Contract
from ..deps import get_erc1155_contract
from ..services import party_service
from ..schemas import (
    PartyCreate, PartyUpdate, PartyGet, PartyTokenBalance, PartyTokenTransfer,
    PartyTokenTransferReceipt
)
from .base_api import BaseAPI

router = InferringRouter()


# noinspection PyTypeChecker
@cbv(router)
class PartyAPI(BaseAPI):
    erc1155_contract: ERC1155Contract = Depends(get_erc1155_contract)
    service = party_service

    @router.get('/')
    async def get_many(
            self, offset: int = 0, limit: int = 20
    ) -> List[PartyGet]:
        return await self._get_many(limit, offset)

    @router.get("/{uid}/")
    async def get_one(
            self, uid: UUID
    ) -> PartyGet:
        return await self._get_one(uid)

    @router.get("/{uid}/token-balance/{token_id}")
    async def get_token_balance(
            self, uid: UUID, token_id: int = Path(0)
    ) -> PartyTokenBalance:
        return await self.service.get_token_balance(
            self.db, self.user, uid, token_id,
            token_contract=self.erc1155_contract
        )

    @router.post("/{uid}/token-transfer/")
    async def transfer_tokens(
            self, uid: UUID, obj: PartyTokenTransfer
    ) -> PartyTokenTransferReceipt:
        return await self.service.transfer_tokens(
            self.db, self.user, uid, obj,
            token_contract=self.erc1155_contract
        )

    @router.post("/")
    async def create_one(
            self, obj: PartyCreate,
            create_blockchain_account: bool = True,
            token_id: int = 0,
            initial_amount: int = 1_000_000_00
    ) -> PartyGet:
        result = await self.service.create(
            self.db, self.user, obj,
            create_blockchain_account=create_blockchain_account,
            token_id=token_id,
            initial_amount=initial_amount,
            token_contract=self.erc1155_contract
        )
        return {**obj.dict(), **result['obj']}

    @router.put("/{uid}/")
    async def update_one(
            self, uid: UUID, obj: PartyUpdate
    ) -> PartyGet:
        return await self._update_one(obj, uid)

    @router.delete("/{uid}/")
    async def delete_one(
            self, uid: UUID
    ) -> APIMessage:
        return await self._delete_one(uid)
