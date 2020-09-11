from databases import Database
from fastapi.encoders import jsonable_encoder
from sqlalchemy.sql import select

from ..db import (catalogs, parties)
from .base_svc import BaseService
from ..schemas import (CatalogCreate, UserInDb)
from .utils import new_uid


class CatalogService(BaseService):
    async def create(self, db: Database, user: UserInDb, obj: CatalogCreate):
        obj_data = jsonable_encoder(obj, exclude_unset=True)
        obj_data['uid'] = new_uid()
        obj_data['seller_id'] = await self.get_id_by_uid(
            db, parties, obj_data['seller_uid']
        )
        del obj_data['seller_uid']
        query = self.table.insert().values(**obj_data)
        async with db.transaction():
            return dict(id=await db.execute(query), uid=obj_data['uid'])

    def _select_query(self):
        return select(
            [catalogs.c.uid, catalogs.c.name, parties.c.uid.label('seller_uid')]
        ).select_from(catalogs.join(parties))


catalog_service = CatalogService(catalogs)
