from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class UserGet:
    """  """

    uid: str
    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False

    def to_dict(self) -> Dict[str, Any]:
        uid = self.uid
        username = self.username
        email = self.email
        name = self.name
        is_active = self.is_active
        is_superuser = self.is_superuser

        return {
            "uid": uid,
            "username": username,
            "email": email,
            "name": name,
            "is_active": is_active,
            "is_superuser": is_superuser,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> UserGet:
        uid = d["uid"]

        username = d.get("username")

        email = d.get("email")

        name = d.get("name")

        is_active = d.get("is_active")

        is_superuser = d.get("is_superuser")

        return UserGet(
            uid=uid, username=username, email=email, name=name, is_active=is_active, is_superuser=is_superuser,
        )
