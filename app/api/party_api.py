from typing import List
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.api_model import APIMessage

from ..services import party_service
from ..schemas import (
    PartyCreate, PartyUpdate, PartyGet,
)
from .base_api import BaseAPI

router = InferringRouter()


# noinspection PyTypeChecker
@cbv(router)
class PartyAPI(BaseAPI):
    service = party_service

    @router.get('/')
    async def get_many(
            self, offset: int = 0, limit: int = 20
    ) -> List[PartyGet]:
        return await self.service.get_many(self.db, self.user, offset, limit)

    @router.get("/{uid}/")
    async def get_one(
            self, uid: str
    ) -> PartyGet:
        return await self.service.get_one_by_uid(self.db, self.user, uid)

    @router.post("/")
    async def create_one(
            self, obj: PartyCreate
    ) -> PartyGet:
        result = await self.service.create(self.db, self.user, obj)
        return {**obj.dict(), **result}

    @router.put("/{uid}/")
    async def update_one(
            self, uid: str, obj: PartyUpdate
    ) -> PartyGet:
        await self.service.update_by_uid(self.db, self.user, uid, obj)
        return {**obj.dict(), "uid": uid}

    @router.delete("/{uid}/")
    async def delete_one(
            self, uid: str
    ) -> APIMessage:
        await self.service.delete_by_uid(self.db, self.user, uid)
        return APIMessage(
            detail=f"Object with uid: {uid} deleted successfully!"
        )
