from __future__ import annotations

from dataclasses import astuple, dataclass
from typing import Any, Dict, Optional

from .types import File


@dataclass
class PartyTokenTransferReceipt:
    """  """

    token_amount: int
    to_uid: str
    data: File
    from_uid: str
    from_address: str
    to_address: str
    txn_hash: str
    token_id: Optional[int] = 0

    def to_dict(self) -> Dict[str, Any]:
        token_amount = self.token_amount
        to_uid = self.to_uid
        data = self.data.to_tuple()

        from_uid = self.from_uid
        from_address = self.from_address
        to_address = self.to_address
        txn_hash = self.txn_hash
        token_id = self.token_id

        return {
            "token_amount": token_amount,
            "to_uid": to_uid,
            "data": data,
            "from_uid": from_uid,
            "from_address": from_address,
            "to_address": to_address,
            "txn_hash": txn_hash,
            "token_id": token_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PartyTokenTransferReceipt:
        token_amount = d["token_amount"]

        to_uid = d["to_uid"]

        data = d["data"]

        from_uid = d["from_uid"]

        from_address = d["from_address"]

        to_address = d["to_address"]

        txn_hash = d["txn_hash"]

        token_id = d.get("token_id")

        return PartyTokenTransferReceipt(
            token_amount=token_amount,
            to_uid=to_uid,
            data=data,
            from_uid=from_uid,
            from_address=from_address,
            to_address=to_address,
            txn_hash=txn_hash,
            token_id=token_id,
        )
