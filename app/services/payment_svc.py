from databases import Database
from fastapi import Depends
from sqlalchemy.sql import select
from loguru import logger

from ..db import (payments, invoices, get_db)
from ..schemas import (PaymentCreate, UserInDb)
from .base_svc import BaseService


class PaymentService(BaseService):
    def __init__(self, db: Database = Depends(get_db)):
        super().__init__(payments, db)

    async def create(self, user: UserInDb, obj: PaymentCreate):
        obj_data = self._to_dict(obj)
        await self._uid_to_fk(obj_data, invoices, 'invoice')
        return await self._insert(obj_data)

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

