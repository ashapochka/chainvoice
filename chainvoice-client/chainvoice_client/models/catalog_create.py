from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CatalogCreate:
    """  """

    name: str
    seller_uid: str

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        seller_uid = self.seller_uid

        return {
            "name": name,
            "seller_uid": seller_uid,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> CatalogCreate:
        name = d["name"]

        seller_uid = d["seller_uid"]

        return CatalogCreate(name=name, seller_uid=seller_uid,)
