from decimal import Decimal
from typing import Optional
from datetime import datetime

from pydantic import condecimal

from .base import (BaseSchema, UIDSchema, UID)


class OrderBase(BaseSchema):
    ref_id: Optional[str] = None
    seller_uid: Optional[UID] = None
    customer_uid: Optional[UID] = None


class OrderCreate(OrderBase):
    seller_uid: UID


class OrderUpdate(OrderBase):
    pass


class OrderGet(OrderBase, UIDSchema):
    amount: Optional[condecimal(
        max_digits=10, decimal_places=2, ge=Decimal(0.0)
    )] = None
    created_at: Optional[datetime]


class OrderAmount(UIDSchema):
    amount: condecimal(
        max_digits=10, decimal_places=2, ge=Decimal(0.0)
    )
