from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import condecimal

from .base import (BaseSchema, UIDSchema, UID)


class PaymentBase(BaseSchema):
    invoice_uid: Optional[UID] = None
    amount: Optional[condecimal(
        max_digits=10, decimal_places=2, ge=Decimal(0.0)
    )] = None
    blockchain_tx_hash: Optional[str] = None


class PaymentCreate(PaymentBase):
    invoice_uid: UID
    amount: condecimal(
        max_digits=10, decimal_places=2, ge=Decimal(0.0)
    )


class PaymentUpdate(PaymentBase):
    pass


class PaymentGet(PaymentBase, UIDSchema):
    paid_at: Optional[datetime]
