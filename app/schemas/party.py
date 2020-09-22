from typing import Optional

from .base import (BaseSchema, UIDSchema)


class PartyBase(BaseSchema):
    name: Optional[str] = None
    blockchain_account_address: Optional[str] = None


class PartyCreate(PartyBase):
    name: str
    blockchain_account_key: Optional[str] = None


class PartyUpdate(PartyBase):
    pass


class PartyGet(PartyBase, UIDSchema):
    pass
