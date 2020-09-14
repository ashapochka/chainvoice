from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CatalogGet:
    """  """

    uid: str
    name: Optional[str] = None
    seller_uid: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid
        name = self.name
        seller_uid = self.seller_uid

        return {
            "uid": uid,
            "name": name,
            "seller_uid": seller_uid,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> CatalogGet:
        uid = d["uid"]

        name = d.get("name")

        seller_uid = d.get("seller_uid")

        return CatalogGet(uid=uid, name=name, seller_uid=seller_uid,)
