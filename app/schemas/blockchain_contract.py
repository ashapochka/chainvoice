from typing import Optional

from .base import (BaseSchema, UIDSchema)


class BlockchainContractBase(BaseSchema):
    name: Optional[str] = None
    contract_address: Optional[str] = None
    contract_code: Optional[str] = None
    contract_abi: Optional[str] = None


class BlockchainContractCreate(BlockchainContractBase):
    name: str


class BlockchainContractUpdate(BlockchainContractBase):
    pass


class BlockchainContractGet(BlockchainContractBase, UIDSchema):
    pass
