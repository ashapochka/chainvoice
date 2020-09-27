from databases import Database
from fastapi import Depends
from sqlalchemy.sql import select

from ..db import (catalogs, parties, get_db)
from .base_svc import BaseService
from ..schemas import (CatalogCreate, UserInDb)


class CatalogService(BaseService):
    def __init__(
            self,
            db: Database = Depends(get_db),
    ):
        super().__init__(catalogs, db)

    async def create(self, user: UserInDb, obj: CatalogCreate):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(obj_data, parties, 'seller')
        return await self._insert(obj_data)

    def _select_query(self):
        return select([
            catalogs.c.uid,
            catalogs.c.name,
            parties.c.uid.label('seller_uid')
        ]).select_from(catalogs.join(parties))

