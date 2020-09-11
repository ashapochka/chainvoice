from typing import Any
from sqlalchemy import Table
from databases import Database
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import select

from ..db import parties
from .utils import new_uid
from ..schemas import UserInDb


class BaseService:
    table: Table = None

    def __init__(self, table: Table):
        self.table = table

    async def get_many(
            self, db: Database, user: UserInDb, offset: int, limit: int
    ):
        query = self._select_query().offset(offset).limit(limit)
        result = await db.fetch_all(query)
        return result

    async def get_one_where(self, db: Database, user: UserInDb, where):
        query = self._select_query().where(where)
        return await db.fetch_one(query)

    def _select_query(self):
        return self.table.select()

    async def get_one(self, db: Database, user: UserInDb, obj_id: Any):
        return await self.get_one_where(db, user, self.table.c.id == obj_id)

    async def get_one_by_uid(self, db: Database, user: UserInDb, uid: str):
        return await self.get_one_where(db, user, self.table.c.uid == str(uid))

    async def create(self, db: Database, user: UserInDb, obj: BaseModel):
        obj_data = jsonable_encoder(obj, exclude_unset=True)
        obj_data['uid'] = new_uid()
        query = self.table.insert().values(**obj_data)
        async with db.transaction():
            return dict(id=await db.execute(query), uid=obj_data['uid'])

    async def update_where(
            self, db: Database, user: UserInDb, where: Any, obj: BaseModel
    ):
        obj_data = jsonable_encoder(obj, exclude_unset=True)
        query = self.table.update().where(where).values(**obj_data)
        async with db.transaction():
            return await db.execute(query)

    async def update(
            self, db: Database, user: UserInDb, obj_id: Any, obj: BaseModel
    ):
        return await self.update_where(db, user, self.table.c.id == obj_id, obj)

    async def update_by_uid(
            self, db: Database, user: UserInDb, uid: str, obj: BaseModel
    ):
        return await self.update_where(
            db, user, self.table.c.uid == str(uid), obj
        )

    async def delete_where(self, db: Database, user: UserInDb, where: Any):
        query = self.table.delete().where(where)
        async with db.transaction():
            return await db.execute(query)

    async def delete(self, db: Database, user: UserInDb, obj_id: Any):
        return await self.delete_where(db, user, self.table.c.id == obj_id)

    async def delete_by_uid(self, db: Database, user: UserInDb, uid: str):
        return await self.delete_where(db, user, self.table.c.uid == str(uid))

    async def get_id_by_uid(self, db: Database, table: Table, uid: str):
        query = select([table.c.id]).where(table.c.uid == str(uid))
        return await db.fetch_val(query, column=0)

