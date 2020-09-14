from databases import Database
from sqlalchemy.sql import select

from ..db import (catalogs, parties)
from .base_svc import BaseService
from ..schemas import (CatalogCreate, UserInDb)


class CatalogService(BaseService):
    async def create(self, db: Database, user: UserInDb, obj: CatalogCreate):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(db, obj_data, parties, 'seller')
        return await self._insert(db, obj_data)

    def _select_query(self):
        return select([
            catalogs.c.uid,
            catalogs.c.name,
            parties.c.uid.label('seller_uid')
        ]).select_from(catalogs.join(parties))


catalog_service = CatalogService(catalogs)
