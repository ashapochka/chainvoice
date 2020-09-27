from uuid import UUID

from fastapi import Depends
from fastapi_utils.api_model import APIMessage

from ..deps import get_current_active_user
from ..schemas import UserInDb
from ..services import BaseService


class BaseAPI:
    user: UserInDb = Depends(get_current_active_user)
    service: BaseService = None

    async def _get_many(self, limit, offset, **kwargs):
        return await self.service.get_many(
            self.user, offset, limit, **kwargs
        )

    async def _get_one(self, uid: UUID):
        return await self.service.get_one_by_uid(self.user, uid)

    async def _create_one(self, obj):
        result = await self.service.create(self.user, obj)
        return {**obj.dict(), **result['obj']}

    async def _update_one(self, obj, uid: UUID):
        await self.service.update_by_uid(self.user, uid, obj)
        return {**obj.dict(), "uid": uid}

    async def _delete_one(self, uid: UUID):
        await self.service.delete_by_uid(self.user, uid)
        return APIMessage(
            detail=f"Object with uid: {uid} deleted successfully!"
        )
