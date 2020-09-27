from databases import Database
from fastapi import Depends
from sqlalchemy.sql import select
from loguru import logger

from ..db import (orders, parties, get_db)
from ..schemas import (OrderCreate, UserInDb)
from .base_svc import BaseService
from .utils import current_time


class OrderService(BaseService):
    def __init__(self, db: Database = Depends(get_db)):
        super().__init__(orders, db)

    async def create(self, user: UserInDb, obj: OrderCreate):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(obj_data, parties, 'seller')
        await self._uid_to_fk(obj_data, parties, 'customer', nullable=True)
        obj_data['created_at'] = current_time()
        return await self._insert(obj_data)

    def _select_query(self):
        sellers = parties.alias()
        customers = parties.alias()
        query = select([
            orders.c.uid,
            orders.c.ref_id,
            sellers.c.uid.label('seller_uid'),
            customers.c.uid.label('customer_uid'),
            orders.c.created_at
        ]).select_from(
            orders.join(
                sellers, orders.c.seller_id == sellers.c.id
            ).outerjoin(
                customers, orders.c.customer_id == customers.c.id
            )
        )
        logger.debug(query)
        return query

