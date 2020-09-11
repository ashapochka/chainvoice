from typing import Optional

from .base import (BaseSchema, UIDSchema, UID)


class CatalogBase(BaseSchema):
    name: Optional[str] = None
    seller_uid: Optional[UID] = None


class CatalogCreate(CatalogBase):
    name: str
    seller_uid: UID


class CatalogUpdate(CatalogBase):
    pass


class CatalogGet(CatalogBase, UIDSchema):
    pass
