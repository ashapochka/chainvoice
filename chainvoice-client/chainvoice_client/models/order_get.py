from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional, cast


@dataclass
class OrderGet:
    """  """

    uid: str
    ref_id: Optional[str] = None
    seller_uid: Optional[str] = None
    customer_uid: Optional[str] = None
    created_at: Optional[datetime.datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid
        ref_id = self.ref_id
        seller_uid = self.seller_uid
        customer_uid = self.customer_uid
        created_at = self.created_at.isoformat() if self.created_at else None

        return {
            "uid": uid,
            "ref_id": ref_id,
            "seller_uid": seller_uid,
            "customer_uid": customer_uid,
            "created_at": created_at,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> OrderGet:
        uid = d["uid"]

        ref_id = d.get("ref_id")

        seller_uid = d.get("seller_uid")

        customer_uid = d.get("customer_uid")

        created_at = None
        if d.get("created_at") is not None:
            created_at = datetime.datetime.fromisoformat(cast(str, d.get("created_at")))

        return OrderGet(
            uid=uid, ref_id=ref_id, seller_uid=seller_uid, customer_uid=customer_uid, created_at=created_at,
        )
