from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class OrderUpdate:
    """  """

    ref_id: Optional[str] = None
    seller_uid: Optional[str] = None
    customer_uid: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id
        seller_uid = self.seller_uid
        customer_uid = self.customer_uid

        return {
            "ref_id": ref_id,
            "seller_uid": seller_uid,
            "customer_uid": customer_uid,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> OrderUpdate:
        ref_id = d.get("ref_id")

        seller_uid = d.get("seller_uid")

        customer_uid = d.get("customer_uid")

        return OrderUpdate(ref_id=ref_id, seller_uid=seller_uid, customer_uid=customer_uid,)
