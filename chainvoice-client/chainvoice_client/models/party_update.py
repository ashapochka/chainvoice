from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PartyUpdate:
    """  """

    name: Optional[str] = None
    blockchain_account_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        blockchain_account_address = self.blockchain_account_address

        return {
            "name": name,
            "blockchain_account_address": blockchain_account_address,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PartyUpdate:
        name = d.get("name")

        blockchain_account_address = d.get("blockchain_account_address")

        return PartyUpdate(name=name, blockchain_account_address=blockchain_account_address,)
