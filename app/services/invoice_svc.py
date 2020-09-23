from databases import Database
from sqlalchemy.sql import select
from loguru import logger

from ..db import (invoices, orders)
from ..schemas import (InvoiceCreate, UserInDb)
from .base_svc import BaseService


class InvoiceService(BaseService):
    async def create(self, db: Database, user: UserInDb, obj: InvoiceCreate):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(db, obj_data, orders, 'order')
        return await self._insert(db, obj_data)

    def _select_query(self):
        query = select([
            invoices.c.uid,
            invoices.c.ref_id,
            orders.c.uid.label('order_uid'),
            invoices.c.due_date,
            invoices.c.state
        ]).select_from(
            invoices.join(orders)
        )
        logger.debug(query)
        return query


invoice_service = InvoiceService(invoices)
