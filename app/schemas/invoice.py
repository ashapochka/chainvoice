from typing import Optional
from datetime import date
from enum import Enum

from .base import (BaseSchema, UIDSchema, UID)


class InvoiceState(str, Enum):
    draft = 'DRAFT'
    unpaid = 'UNPAID'
    paid = 'PAID'
    canceled = 'CANCELED'


class InvoiceBase(BaseSchema):
    ref_id: Optional[str] = None
    order_uid: Optional[UID] = None
    due_date: Optional[date] = None
    state: Optional[InvoiceState] = InvoiceState.draft


class InvoiceCreate(InvoiceBase):
    order_uid: UID
    state: InvoiceState = InvoiceState.draft


class InvoiceUpdate(InvoiceBase):
    pass


class InvoiceGet(InvoiceBase, UIDSchema):
    pass
