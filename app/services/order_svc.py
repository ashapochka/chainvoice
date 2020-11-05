from decimal import Decimal

from databases import Database
from fastapi import Depends
from sqlalchemy.sql import select
from sqlalchemy import desc, func

# from loguru import logger

from .order_item_svc import OrderItemService
from ..db import (orders, order_items, parties, get_db)
from ..schemas import (OrderCreate, UserInDb)
from .base_svc import BaseService
from .utils import current_time


class OrderService(BaseService):
    def __init__(
            self,
            db: Database = Depends(get_db),
            order_item_service: OrderItemService = Depends(),
    ):
        super().__init__(orders, db)
        self.order_item_service = order_item_service

    async def create(self, user: UserInDb, obj: OrderCreate):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(obj_data, parties, 'seller')
        await self._uid_to_fk(obj_data, parties, 'customer', nullable=True)
        obj_data['created_at'] = current_time()
        return await self._insert(obj_data)

    async def get_total_amount(self, user: UserInDb, uid) -> Decimal:
        return await self.order_item_service.get_order_amount(user, uid)

    # noinspection PyUnusedLocal
    async def update_total_amount(self, user: UserInDb, uid):
        amount_calc_stmt = select(
            [func.sum(order_items.c.quantity * order_items.c.base_price)]
        ).where(
            order_items.c.order_id == orders.c.id
        )
        where_uid = orders.c.uid == str(uid)
        query = orders.update().where(where_uid).values(
            amount=amount_calc_stmt
        ).returning(
            orders.c.uid,
            orders.c.amount
        )
        async with self.db.transaction():
            return await self.db.fetch_one(query)

    def _select_query(self):
        sellers = parties.alias()
        customers = parties.alias()
        from_query = select([
            orders.c.uid.label('uid'),
            orders.c.ref_id.label('ref_id'),
            orders.c.amount.label('amount'),
            sellers.c.uid.label('seller_uid'),
            sellers.c.name.label('seller_name'),
            customers.c.uid.label('customer_uid'),
            customers.c.name.label('customer_name'),
            orders.c.created_at.label('created_at')
        ]).select_from(
            orders.join(
                sellers, orders.c.seller_id == sellers.c.id
            ).outerjoin(
                customers, orders.c.customer_id == customers.c.id
            )
        ).alias('from_query')
        query = select(from_query.c).select_from(from_query).order_by(
            desc(from_query.c.created_at)
        )
        return query
