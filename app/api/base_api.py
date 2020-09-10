from typing import (List, Generic, TypeVar)
from fastapi import Depends
from databases import Database

from ..deps import (get_db, get_current_active_user)
from ..schemas import  UserInDb

SchemaGet = TypeVar('SchemaGet')
SchemaCreate = TypeVar('SchemaCreate')
SchemaUpdate = TypeVar('SchemaUpdate')


# noinspection PyTypeChecker
class BaseAPI(Generic[SchemaGet, SchemaCreate, SchemaUpdate]):
    db: Database = Depends(get_db)
    user: UserInDb = Depends(get_current_active_user)
    service = None

    async def get_many(
            self, offset: int = 0, limit: int = 20
    ) -> List[SchemaGet]:
        return await self.service.get_many(self.db, self.user, offset, limit)

    async def get_one(
            self, uid: str
    ) -> SchemaGet:
        return await self.service.get_one_by_uid(self.db, self.user, uid)

    async def create_one(
            self, obj: SchemaCreate
    ) -> SchemaGet:
        result = await self.service.create(self.db, self.user, obj)
        return {**obj.dict(), **result}

    async def update_one(
            self, uid: str, obj: SchemaUpdate
    ) -> SchemaGet:
        await self.service.update_by_uid(self.db, self.user, uid, obj)
        return {**obj.dict(), "uid": uid}

    async def delete_one(
            self, uid: str
    ):
        await self.service.delete_by_uid(self.db, self.user, uid)
        return {
            "message": "Object with uid: {} deleted successfully!".format(uid)}
