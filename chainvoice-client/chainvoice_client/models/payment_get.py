from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional, cast


@dataclass
class PaymentGet:
    """  """

    uid: str
    invoice_uid: Optional[str] = None
    amount: Optional[float] = None
    blockchain_tx_address: Optional[str] = None
    created_at: Optional[datetime.datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid
        invoice_uid = self.invoice_uid
        amount = self.amount
        blockchain_tx_address = self.blockchain_tx_address
        created_at = self.created_at.isoformat() if self.created_at else None

        return {
            "uid": uid,
            "invoice_uid": invoice_uid,
            "amount": amount,
            "blockchain_tx_address": blockchain_tx_address,
            "created_at": created_at,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PaymentGet:
        uid = d["uid"]

        invoice_uid = d.get("invoice_uid")

        amount = d.get("amount")

        blockchain_tx_address = d.get("blockchain_tx_address")

        created_at = None
        if d.get("created_at") is not None:
            created_at = datetime.datetime.fromisoformat(cast(str, d.get("created_at")))

        return PaymentGet(
            uid=uid,
            invoice_uid=invoice_uid,
            amount=amount,
            blockchain_tx_address=blockchain_tx_address,
            created_at=created_at,
        )
