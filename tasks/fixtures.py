from typing import List, Optional

from pydantic import BaseModel

from app.schemas import (
    PartyBase, CatalogBase, CatalogItemBase
)


class CatalogItemFixture(CatalogItemBase):
    pass


class CatalogFixture(CatalogBase):
    catalog_items: Optional[List[CatalogItemFixture]]


class PartyFixture(PartyBase):
    catalogs: Optional[List[CatalogFixture]]


class RootPartiesFixture(BaseModel):
    parties: Optional[List[PartyFixture]]
