from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CatalogItemUpdate:
    """  """

    name: Optional[str] = None
    catalog_uid: Optional[str] = None
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
    def from_dict(d: Dict[str, Any]) -> CatalogItemUpdate:
        name = d.get("name")

        catalog_uid = d.get("catalog_uid")

        price = d.get("price")

        return CatalogItemUpdate(name=name, catalog_uid=catalog_uid, price=price,)
