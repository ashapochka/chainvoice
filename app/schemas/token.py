from typing import Optional
from pydantic import BaseModel

from .base import UID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[UID] = None
