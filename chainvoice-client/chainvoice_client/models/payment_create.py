from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PaymentCreate:
    """  """

    invoice_uid: str
    amount: float
    blockchain_tx_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        invoice_uid = self.invoice_uid
        amount = self.amount
        blockchain_tx_address = self.blockchain_tx_address

        return {
            "invoice_uid": invoice_uid,
            "amount": amount,
            "blockchain_tx_address": blockchain_tx_address,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PaymentCreate:
        invoice_uid = d["invoice_uid"]

        amount = d["amount"]

        blockchain_tx_address = d.get("blockchain_tx_address")

        return PaymentCreate(invoice_uid=invoice_uid, amount=amount, blockchain_tx_address=blockchain_tx_address,)
