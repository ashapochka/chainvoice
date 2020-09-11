from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class APIMessage:
    """ A lightweight utility class intended for use with simple message-returning endpoints. """

    detail: str

    def to_dict(self) -> Dict[str, Any]:
        detail = self.detail

        return {
            "detail": detail,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> APIMessage:
        detail = d["detail"]

        return APIMessage(detail=detail,)
