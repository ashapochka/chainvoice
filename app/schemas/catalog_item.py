from typing import Optional
from decimal import Decimal
from pydantic import condecimal

from .base import (BaseSchema, UIDSchema, UID)


class CatalogItemBase(BaseSchema):
    name: Optional[str] = None
    catalog_uid: Optional[UID] = None
    price: Optional[condecimal(
        max_digits=10, decimal_places=2, ge=Decimal(0.0)
    )] = None


class CatalogItemCreate(CatalogItemBase):
    name: str
    catalog_uid: UID


class CatalogItemUpdate(CatalogItemBase):
    pass


class CatalogItemGet(CatalogItemBase, UIDSchema):
    pass
