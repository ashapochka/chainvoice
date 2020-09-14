from databases import Database
from sqlalchemy.sql import select
from loguru import logger

from ..db import (payments, invoices)
from ..schemas import (PaymentCreate, UserInDb)
from .base_svc import BaseService


class PaymentService(BaseService):
    async def create(self, db: Database, user: UserInDb, obj: PaymentCreate):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(db, obj_data, invoices, 'invoice')
        return await self._insert(db, obj_data)

    def _select_query(self):
        query = select([
            payments.c.uid,
            invoices.c.uid.label('invoice_uid'),
            payments.c.amount,
            payments.c.paid_at,
            payments.c.blockchain_tx_address
        ]).select_from(
            payments.join(invoices)
        )
        logger.debug(query)
        return query


payment_service = PaymentService(payments)
