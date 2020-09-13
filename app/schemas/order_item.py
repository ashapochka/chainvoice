from typing import Optional
from decimal import Decimal
from pydantic import (condecimal, conint)

from .base import (BaseSchema, UIDSchema, UID)


class OrderItemBase(BaseSchema):
    order_uid: Optional[UID] = None
    catalog_item_uid: Optional[UID] = None
    quantity: Optional[conint(ge=0)] = 1
    base_price: Optional[condecimal(
        max_digits=10, decimal_places=2, ge=Decimal(0.0)
    )] = None


class OrderItemCreate(OrderItemBase):
    order_uid: UID
    catalog_item_uid: UID
    quantity: conint(ge=0) = 1


class OrderItemUpdate(OrderItemBase):
    pass


class OrderItemGet(OrderItemBase, UIDSchema):
    pass
