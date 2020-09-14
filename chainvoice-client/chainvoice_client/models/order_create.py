from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OrderCreate:
    """  """

    seller_uid: str
    ref_id: Optional[str] = None
    customer_uid: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        seller_uid = self.seller_uid
        ref_id = self.ref_id
        customer_uid = self.customer_uid

        return {
            "seller_uid": seller_uid,
            "ref_id": ref_id,
            "customer_uid": customer_uid,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> OrderCreate:
        seller_uid = d["seller_uid"]

        ref_id = d.get("ref_id")

        customer_uid = d.get("customer_uid")

        return OrderCreate(seller_uid=seller_uid, ref_id=ref_id, customer_uid=customer_uid,)
