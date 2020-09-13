from typing import Optional
from datetime import datetime

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
    created_at: datetime
