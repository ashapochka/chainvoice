from typing import Optional

from .base import (BaseSchema, UIDSchema, UID)


class BlockchainContractBase(BaseSchema):
    owner_uid: Optional[UID] = None
    name: Optional[str] = None
    contract_address: Optional[str] = None
    contract_code: Optional[str] = None
    contract_abi: Optional[str] = None


class BlockchainContractCreate(BlockchainContractBase):
    name: str
    owner_uid: UID


class BlockchainContractUpdate(BlockchainContractBase):
    pass


class BlockchainContractGet(BlockchainContractBase, UIDSchema):
    pass
