from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PartyCreate:
    """ Intended for use as a base class for externally-facing models.

Any models that inherit from this class will:
* accept fields using snake_case or camelCase keys
* use camelCase keys in the generated OpenAPI spec
* have orm_mode on by default
    * Because of this, FastAPI will automatically attempt to parse returned orm instances into the model """

    name: str
    blockchain_account_address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        blockchain_account_address = self.blockchain_account_address

        return {
            "name": name,
            "blockchainAccountAddress": blockchain_account_address,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> PartyCreate:
        name = d["name"]

        blockchain_account_address = d.get("blockchainAccountAddress")

        return PartyCreate(name=name, blockchain_account_address=blockchain_account_address,)
