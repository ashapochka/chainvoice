from databases import Database
from sqlalchemy.sql import select

from ..db import (order_items, orders, catalog_items)
from .base_svc import BaseService
from ..schemas import (OrderItemCreate, UserInDb)


class OrderItemService(BaseService):
    async def create(self, db: Database, user: UserInDb, obj: OrderItemCreate):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(db, obj_data, orders, 'order')
        await self._uid_to_fk(db, obj_data, catalog_items, 'catalog_item')
        return await self._insert(db, obj_data)

    def _select_query(self):
        return select([
            order_items.c.uid,
            order_items.c.quantity,
            order_items.c.base_price,
            orders.c.uid.label('order_uid'),
            catalog_items.c.uid.label('catalog_item_uid')
        ]).select_from(
            order_items.join(orders).join(catalog_items)
        )


order_item_service = OrderItemService(order_items)
