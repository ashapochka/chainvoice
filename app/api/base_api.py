from fastapi import Depends
from databases import Database

from ..deps import (get_db, get_current_active_user)
from ..schemas import  UserInDb


class BaseAPI:
    db: Database = Depends(get_db)
    user: UserInDb = Depends(get_current_active_user)

    async def _get_many(self, limit, offset, **kwargs):
        return await self.service.get_many(
            self.db, self.user, offset, limit, **kwargs
        )

    async def _get_one(self, uid):
        return await self.service.get_one_by_uid(self.db, self.user, uid)

    async def _create_one(self, obj):
        result = await self.service.create(self.db, self.user, obj)
        return {**obj.dict(), **result['obj']}

    async def _update_one(self, obj, uid):
        await self.service.update_by_uid(self.db, self.user, uid, obj)
        return {**obj.dict(), "uid": uid}

    async def _delete_one(self, uid):
        await self.service.delete_by_uid(self.db, self.user, uid)
        return APIMessage(
            detail=f"Object with uid: {uid} deleted successfully!"
        )
