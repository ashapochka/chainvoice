from decimal import Decimal

from databases import Database
from fastapi import Depends
from sqlalchemy.sql import select

from .utils import to_money
from ..db import (order_items, orders, catalog_items, get_db)
from .base_svc import BaseService
from ..schemas import (OrderItemCreate, UserInDb)


class OrderItemService(BaseService):
    def __init__(self, db: Database = Depends(get_db)):
        super().__init__(order_items, db)

    async def create(
            self, user: UserInDb, obj: OrderItemCreate, tx: bool = True
    ):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(obj_data, orders, 'order')
        await self._uid_to_fk(obj_data, catalog_items, 'catalog_item')
        return await self._insert(obj_data, tx=tx)

    async def get_order_amount(
            self, user: UserInDb, order_uid, offset: int = 0, limit: int = 1000
    ) -> Decimal:
        items = await self.get_many(
            user, offset, limit, order_uid=str(order_uid)
        )
        total_amount = sum(
            item['base_price'] * item['quantity'] for item in items
        )
        return to_money(total_amount)

    def _select_query(self):
        from_query = select([
            order_items.c.uid.label('uid'),
            order_items.c.quantity.label('quantity'),
            order_items.c.base_price.label('base_price'),
            orders.c.uid.label('order_uid'),
            catalog_items.c.uid.label('catalog_item_uid'),
            catalog_items.c.name.label('catalog_item_name')
        ]).select_from(
            order_items.join(orders).join(catalog_items)
        ).alias('from_query')
        query = select(from_query.c).select_from(from_query)
        return query
