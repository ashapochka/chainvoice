from databases import Database
from sqlalchemy.sql import select

from ..db import (catalog_items, catalogs)
from .base_svc import BaseService
from ..schemas import (CatalogItemCreate, UserInDb)


class CatalogItemService(BaseService):
    async def create(self, db: Database, user: UserInDb, obj: CatalogItemCreate):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(db, obj_data, catalogs, 'catalog')
        return await self._insert(db, obj_data)

    def _select_query(self):
        return select([
            catalog_items.c.uid,
            catalog_items.c.name,
            catalog_items.c.price,
            catalogs.c.uid.label('catalog_uid')
        ]).select_from(catalog_items.join(catalogs))


catalog_item_service = CatalogItemService(catalog_items)
