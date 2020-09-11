from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Token:
    """  """

    access_token: str
    token_type: str

    def to_dict(self) -> Dict[str, Any]:
        access_token = self.access_token
        token_type = self.token_type

        return {
            "access_token": access_token,
            "token_type": token_type,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> Token:
        access_token = d["access_token"]

        token_type = d["token_type"]

        return Token(access_token=access_token, token_type=token_type,)
