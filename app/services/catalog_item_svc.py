from databases import Database
from fastapi import Depends
from sqlalchemy.sql import select

from ..db import (catalog_items, catalogs, get_db)
from .base_svc import BaseService
from ..schemas import (CatalogItemCreate, UserInDb)


class CatalogItemService(BaseService):
    def __init__(
            self,
            db: Database = Depends(get_db),
    ):
        super().__init__(catalog_items, db)

    async def create(self, user: UserInDb, obj: CatalogItemCreate):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(obj_data, catalogs, 'catalog')
        return await self._insert(obj_data)

    def _select_query(self):
        catalogs_items = select([
            catalog_items.c.uid.label('uid'),
            catalog_items.c.name.label('name'),
            catalog_items.c.price.label('price'),
            catalogs.c.uid.label('catalog_uid')
        ]).select_from(catalog_items.join(catalogs)).alias('catalogs_items')
        query = select([
            catalogs_items.c.uid.label('uid'),
            catalogs_items.c.name.label('name'),
            catalogs_items.c.price.label('price'),
            catalogs_items.c.catalog_uid.label('catalog_uid')
        ]).select_from(catalogs_items)
        return query
