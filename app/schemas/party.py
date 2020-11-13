from typing import Optional

from pydantic import (SecretStr, conint)

from .base import (BaseSchema, UIDSchema, UID)


class PartyBase(BaseSchema):
    name: Optional[str] = None
    blockchain_account_address: Optional[str] = None
    active: Optional[bool] = True


class PartyCreate(PartyBase):
    name: str
    blockchain_account_key: Optional[SecretStr] = None


class PartyUpdate(PartyBase):
    pass


class PartyGet(PartyBase, UIDSchema):
    pass


class TokenAmount(BaseSchema):
    token_amount: conint(ge=0)
    token_id: conint(ge=0, le=0) = 0


class PartyTokenBalance(PartyGet, TokenAmount):
    pass


class PartyTokenTransfer(TokenAmount):
    token_amount: conint(gt=0)
    to_uid: UID
    data: str


class PartyTokenTransferReceipt(PartyTokenTransfer):
    from_uid: UID
    from_address: str
    to_address: str
    txn_hash: str
    txn_status: int
