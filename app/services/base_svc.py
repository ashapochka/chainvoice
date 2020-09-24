from typing import Any
from uuid import UUID

from databases import Database
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import (Table, and_)
from sqlalchemy.sql import select
from loguru import logger

from .utils import new_uid, raise_not_found_if_none
from ..schemas import UserInDb


# noinspection PyPropertyAccess
class BaseService:
    table: Table = None

    def __init__(self, table: Table):
        self.table = table

    async def get_many(
            self, db: Database, user: UserInDb,
            offset: int, limit: int,
            **kwargs
    ):
        query = self._select_query()
        logger.debug(query)
        if len(kwargs):
            query_alias = query.alias()
            where_clauses = [query_alias.c[key] == value for (key, value) in
                             kwargs.items() if value is not None]
            if len(where_clauses):
                query = query.where(and_(*where_clauses))
                logger.debug(query)
        query = query.offset(offset).limit(limit)
        logger.debug(query)
        result = await db.fetch_all(query)
        return result

    async def get_one_where(self, db: Database, user: UserInDb, where):
        query = self._select_query().where(where)
        return await db.fetch_one(query)

    def _select_query(self):
        return self.table.select()

    async def get_one(self, db: Database, user: UserInDb, obj_id: Any):
        return await self.get_one_where(db, user, self.table.c.id == obj_id)

    async def get_one_by_uid(
            self, db: Database, user: UserInDb, uid: UUID,
            raise_not_found: bool = False,
            what=None,
            msg=None
    ):
        obj = await self.get_one_where(db, user, self.table.c.uid == str(uid))
        if raise_not_found:
            if not what:
                what = self.table.name
            raise_not_found_if_none(obj, what=what, by=uid, msg=msg)
        return obj

    async def get_one_by_name(self, db: Database, user: UserInDb, name: str):
        return await self.get_one_where(db, user, self.table.c.name == str(name))

    async def create(self, db: Database, user: UserInDb, obj: BaseModel):
        obj_data = self._to_dict(obj)
        return await self._insert(db, obj_data)

    @staticmethod
    def _to_dict(obj):
        return jsonable_encoder(obj, exclude_unset=True)

    async def _insert(self, db, obj_data):
        obj_data['uid'] = new_uid()
        query = self.table.insert().values(**obj_data)
        async with db.transaction():
            return dict(id=await db.execute(query), obj=obj_data)

    async def update_where(
            self, db: Database, user: UserInDb, where: Any, obj: BaseModel
    ):
        obj_data = self._to_dict(obj)
        query = self.table.update().where(where).values(**obj_data)
        async with db.transaction():
            return await db.execute(query)

    async def update(
            self, db: Database, user: UserInDb, obj_id: Any, obj: BaseModel
    ):
        return await self.update_where(db, user, self.table.c.id == obj_id, obj)

    async def update_by_uid(
            self, db: Database, user: UserInDb, uid: UUID, obj: BaseModel
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

    async def delete_by_uid(self, db: Database, user: UserInDb, uid: UUID):
        return await self.delete_where(db, user, self.table.c.uid == str(uid))

    @staticmethod
    async def get_id_by_uid(db: Database, table: Table, uid: UUID):
        query = select([table.c.id]).where(table.c.uid == str(uid))
        return await db.fetch_val(query, column=0)

    async def _uid_to_fk(
            self, db, obj_data, parent_table, prefix, nullable=False
    ):
        uid_name = f'{prefix}_uid'
        fk_name = f'{prefix}_id'
        if nullable and uid_name not in obj_data:
            return
        obj_data[fk_name] = await self.get_id_by_uid(
            db, parent_table, obj_data[uid_name]
        )
        del obj_data[uid_name]
