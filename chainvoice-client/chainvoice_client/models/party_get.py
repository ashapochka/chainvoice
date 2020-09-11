from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PartyGet:
    """  """

    uid: str
    name: Optional[str] = None
    blockchain_account_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid
        name = self.name
        blockchain_account_address = self.blockchain_account_address

        return {
            "uid": uid,
            "name": name,
            "blockchain_account_address": blockchain_account_address,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PartyGet:
        uid = d["uid"]

        name = d.get("name")

        blockchain_account_address = d.get("blockchain_account_address")

        return PartyGet(uid=uid, name=name, blockchain_account_address=blockchain_account_address,)
