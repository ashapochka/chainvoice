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


class OrderAmount(UIDSchema):
    amount: Optional[condecimal(
        max_digits=10, decimal_places=2, ge=Decimal(0.0)
    )] = None


class OrderGet(OrderBase, OrderAmount, UIDSchema):
    seller_name: Optional[str] = None
    customer_name: Optional[str] = None
    created_at: Optional[datetime] = None,
    invoiced: Optional[bool] = None
