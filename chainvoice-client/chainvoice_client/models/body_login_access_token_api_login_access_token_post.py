from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class BodyLoginAccessTokenApiLoginAccessTokenPost:
    """  """

    username: str
    password: str
    grant_type: Optional[str] = None
    scope: Optional[str] = ""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        username = self.username
        password = self.password
        grant_type = self.grant_type
        scope = self.scope
        client_id = self.client_id
        client_secret = self.client_secret

        return {
            "username": username,
            "password": password,
            "grant_type": grant_type,
            "scope": scope,
            "client_id": client_id,
            "client_secret": client_secret,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> BodyLoginAccessTokenApiLoginAccessTokenPost:
        username = d["username"]

        password = d["password"]

        grant_type = d.get("grant_type")

        scope = d.get("scope")

        client_id = d.get("client_id")

        client_secret = d.get("client_secret")

        return BodyLoginAccessTokenApiLoginAccessTokenPost(
            username=username,
            password=password,
            grant_type=grant_type,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )
