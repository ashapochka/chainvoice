from __future__ import annotations

from dataclasses import astuple, dataclass
from typing import Any, Dict, Optional

from .types import File


@dataclass
class PartyTokenTransfer:
    """  """

    token_amount: int
    to_uid: str
    data: File
    token_id: Optional[int] = 0

    def to_dict(self) -> Dict[str, Any]:
        token_amount = self.token_amount
        to_uid = self.to_uid
        data = self.data.to_tuple()

        token_id = self.token_id

        return {
            "token_amount": token_amount,
            "to_uid": to_uid,
            "data": data,
            "token_id": token_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PartyTokenTransfer:
        token_amount = d["token_amount"]

        to_uid = d["to_uid"]

        data = d["data"]

        token_id = d.get("token_id")

        return PartyTokenTransfer(token_amount=token_amount, to_uid=to_uid, data=data, token_id=token_id,)
