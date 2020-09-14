from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CatalogUpdate:
    """  """

    name: Optional[str] = None
    seller_uid: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        seller_uid = self.seller_uid

        return {
            "name": name,
            "seller_uid": seller_uid,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> CatalogUpdate:
        name = d.get("name")

        seller_uid = d.get("seller_uid")

        return CatalogUpdate(name=name, seller_uid=seller_uid,)
