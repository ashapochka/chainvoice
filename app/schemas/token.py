from typing import Optional

from .base import (BaseSchema, UID)


class Token(BaseSchema):
    access_token: str
    token_type: str


class TokenPayload(BaseSchema):
    sub: Optional[UID] = None
