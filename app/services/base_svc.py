from typing import Any
from sqlalchemy import Table
from databases import Database
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import UUID

from ..db import parties
from .utils import new_uid


class BaseService:
    table: Table = None

    def __init__(self, table: Table):
        self.table = table

    async def get_many(self, db: Database, offset: int, limit: int):
        query = self.table.select().offset(offset).limit(limit)
        result = await db.fetch_all(query)
        return result

    async def get_one_where(self, db: Database, where):
        query = self.table.select().where(where)
        return await db.fetch_one(query)

    async def get_one(self, db: Database, obj_id: Any):
        return await self.get_one_where(db, self.table.c.id == obj_id)

    async def get_one_by_uid(self, db: Database, uid: str):
        return await self.get_one_where(db, self.table.c.uid == str(uid))

    async def create(self, db: Database, obj: BaseModel):
        obj_data = jsonable_encoder(obj, exclude_unset=True)
        obj_data['uid'] = new_uid()
        query = self.table.insert().values(**obj_data)
        async with db.transaction():
            return dict(id=await db.execute(query), uid=obj_data['uid'])

    async def update_where(self, db: Database, where: Any, obj: BaseModel):
        obj_data = jsonable_encoder(obj, exclude_unset=True)
        query = self.table.update().where(where).values(**obj_data)
        async with db.transaction():
            return await db.execute(query)

    async def update(self, db: Database, id: Any, obj: BaseModel):
        return await self.update_where(db, self.table.c.id == id, obj)

    async def update_by_uid(self, db: Database, uid: str, obj: BaseModel):
        return await self.update_where(db, self.table.c.uid == uid, obj)

    async def delete(self, db: Database, id: Any):
        query = self.table.delete().where(self.table.c.id == id)
        async with db.transaction():
            return await db.execute(query)

    async def delete_by_uid(self, db: Database, uid: str):
        query = self.table.delete().where(self.table.c.uid == uid)
        async with db.transaction():
            return await db.execute(query)

