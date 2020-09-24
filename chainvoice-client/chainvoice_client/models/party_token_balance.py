from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PartyTokenBalance:
    """  """

    token_amount: int
    uid: str
    token_id: Optional[int] = 0
    name: Optional[str] = None
    blockchain_account_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        token_amount = self.token_amount
        uid = self.uid
        token_id = self.token_id
        name = self.name
        blockchain_account_address = self.blockchain_account_address

        return {
            "token_amount": token_amount,
            "uid": uid,
            "token_id": token_id,
            "name": name,
            "blockchain_account_address": blockchain_account_address,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PartyTokenBalance:
        token_amount = d["token_amount"]

        uid = d["uid"]

        token_id = d.get("token_id")

        name = d.get("name")

        blockchain_account_address = d.get("blockchain_account_address")

        return PartyTokenBalance(
            token_amount=token_amount,
            uid=uid,
            token_id=token_id,
            name=name,
            blockchain_account_address=blockchain_account_address,
        )
