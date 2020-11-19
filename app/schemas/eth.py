from pydantic import BaseModel
from typing import List, Optional


class TransactionInputGet(BaseModel):
    contract: Optional[str]
    address: str
    function: str
    args: dict


class TransactionEventGet(BaseModel):
    name: str
    args: dict
    address: str
    log_index: int


class TransactionGet(BaseModel):
    hash: str
    block_number: int
    index_in_block: int
    from_address: str
    to_address: str
    input: TransactionInputGet
    events: List[TransactionEventGet]
