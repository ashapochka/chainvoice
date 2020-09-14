from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PaymentUpdate:
    """  """

    invoice_uid: Optional[str] = None
    amount: Optional[float] = None
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
    def from_dict(d: Dict[str, Any]) -> PaymentUpdate:
        invoice_uid = d.get("invoice_uid")

        amount = d.get("amount")

        blockchain_tx_address = d.get("blockchain_tx_address")

        return PaymentUpdate(invoice_uid=invoice_uid, amount=amount, blockchain_tx_address=blockchain_tx_address,)
