from loguru import logger
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

    async def create(self, user: UserInDb, obj: CatalogCreate, tx: bool = True):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(obj_data, parties, 'seller')
        return await self._insert(obj_data, tx=tx)

    def _select_query(self):
        party_catalogs = select([
            catalogs.c.uid.label('uid'),
            catalogs.c.name.label('name'),
            parties.c.uid.label('seller_uid')
        ]).select_from(catalogs.join(parties)).alias('party_catalogs')
        query = select([
            party_catalogs.c.uid.label('uid'),
            party_catalogs.c.name.label('name'),
            party_catalogs.c.seller_uid.label('seller_uid')
        ]).select_from(party_catalogs)
        return query
