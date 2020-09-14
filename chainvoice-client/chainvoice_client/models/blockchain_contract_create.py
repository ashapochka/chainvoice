from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class BlockchainContractCreate:
    """  """

    name: str
    contract_address: Optional[str] = None
    contract_code: Optional[str] = None
    contract_abi: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        contract_address = self.contract_address
        contract_code = self.contract_code
        contract_abi = self.contract_abi

        return {
            "name": name,
            "contract_address": contract_address,
            "contract_code": contract_code,
            "contract_abi": contract_abi,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> BlockchainContractCreate:
        name = d["name"]

        contract_address = d.get("contract_address")

        contract_code = d.get("contract_code")

        contract_abi = d.get("contract_abi")

        return BlockchainContractCreate(
            name=name, contract_address=contract_address, contract_code=contract_code, contract_abi=contract_abi,
        )
