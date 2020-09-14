from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CatalogItemCreate:
    """  """

    name: str
    catalog_uid: str
    price: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        catalog_uid = self.catalog_uid
        price = self.price

        return {
            "name": name,
            "catalog_uid": catalog_uid,
            "price": price,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> CatalogItemCreate:
        name = d["name"]

        catalog_uid = d["catalog_uid"]

        price = d.get("price")

        return CatalogItemCreate(name=name, catalog_uid=catalog_uid, price=price,)
