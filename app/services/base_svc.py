from typing import Any

from databases import Database
from pydantic import BaseModel
from sqlalchemy import (Table, and_)
from sqlalchemy.sql import select
from loguru import logger

from .utils import (new_uid, raise_not_found_if_none)
from ..schemas import UserInDb


# noinspection PyPropertyAccess
class BaseService:
    table: Table = None
    db: Database = None

    def __init__(self, table: Table, db: Database):
        self.table = table
        self.db = db
        self.query = self._select_query()

    async def get_many(
            self, user: UserInDb,
            offset: int, limit: int,
            **kwargs
    ):
        logger.debug(kwargs)
        query = self.query
        logger.debug(query)
        if len(kwargs):
            query_from = query.froms[0]
            where_clauses = [
                query_from.c[key] == value for (key, value) in
                kwargs.items() if value is not None
            ]
            if len(where_clauses):
                query = query.where(and_(*where_clauses))
        query = query.offset(offset).limit(limit)
        logger.debug(query)
        result = await self.db.fetch_all(query)
        return result

    async def get_one_where(self, user: UserInDb, where):
        query = self.query.where(where)
        logger.debug(query)
        return await self.db.fetch_one(query)

    def _select_query(self):
        return self.table.select()

    async def get_one(self, user: UserInDb, obj_id: Any):
        return await self.get_one_where(
            user, self.query.froms[0].c.id == obj_id
        )

    async def get_one_by_uid(
            self, user: UserInDb, uid,
            raise_not_found: bool = False,
            what=None,
            msg=None
    ):
        obj = await self.get_one_where(
            user, self.query.froms[0].c.uid == str(uid)
        )
        if raise_not_found:
            if not what:
                what = self.table.name
            raise_not_found_if_none(obj, what=what, by=uid, msg=msg)
        return obj

    async def get_one_by_name(self, user: UserInDb, name: str):
        return await self.get_one_where(
            user, self.query.froms[0].c.name == str(name)
        )

    async def create(self, user: UserInDb, obj: BaseModel, tx: bool = True):
        obj_data = self._to_dict(obj)
        return await self._insert(obj_data, tx=tx)

    @staticmethod
    def _to_dict(obj):
        return obj.dict(exclude_unset=True)

    async def _execute_in_tx(self, tx, func):
        if tx:
            async with self.db.transaction():
                return await func()
        else:
            return await func()

    async def _insert(self, obj_data, tx: bool = True):
        if 'uid' not in obj_data:
            obj_data['uid'] = new_uid()
        query = self.table.insert().values(**obj_data)

        async def f():
            return dict(id=await self.db.execute(query), obj=obj_data)
        return await self._execute_in_tx(tx, f)
        # async with self.db.transaction():
        #     return dict(id=await self.db.execute(query), obj=obj_data)

    async def update_where(
            self, user: UserInDb, where: Any, obj: BaseModel, tx: bool = True
    ):
        obj_data = self._to_dict(obj)
        query = self.table.update().where(where).values(**obj_data)

        async def f():
            return await self.db.execute(query)
        return await self._execute_in_tx(tx, f)
        # async with self.db.transaction():
        #     return await self.db.execute(query)

    async def update(
            self, user: UserInDb, obj_id: Any, obj: BaseModel, tx: bool = True
    ):
        return await self.update_where(
            user, self.table.c.id == obj_id, obj, tx=tx
        )

    async def update_by_uid(
            self, user: UserInDb, uid, obj: BaseModel, tx: bool = True
    ):
        return await self.update_where(
            user, self.table.c.uid == str(uid), obj, tx=tx
        )

    async def delete_where(self, user: UserInDb, where: Any, tx: bool = True):
        query = self.table.delete().where(where)

        async def f():
            return await self.db.execute(query)
        return await self._execute_in_tx(tx, f)
        # async with self.db.transaction():
        #     return await self.db.execute(query)

    async def delete(self, user: UserInDb, obj_id: Any, tx: bool = True):
        return await self.delete_where(user, self.table.c.id == obj_id, tx=tx)

    async def delete_by_uid(self, user: UserInDb, uid, tx: bool = True):
        return await self.delete_where(
            user, self.table.c.uid == str(uid), tx=tx
        )

    async def get_id_by_uid(self, table: Table, uid):
        query = select([table.c.id]).where(table.c.uid == str(uid))
        return await self.db.fetch_val(query, column=0)

    async def _uid_to_fk(
            self, obj_data, parent_table, prefix, nullable=False
    ):
        uid_name = f'{prefix}_uid'
        fk_name = f'{prefix}_id'
        if nullable and uid_name not in obj_data:
            return
        obj_data[fk_name] = await self.get_id_by_uid(
            parent_table, obj_data[uid_name]
        )
        del obj_data[uid_name]
