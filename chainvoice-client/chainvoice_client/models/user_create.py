from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class UserCreate:
    """  """

    username: str
    password: str
    email: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False

    def to_dict(self) -> Dict[str, Any]:
        username = self.username
        password = self.password
        email = self.email
        name = self.name
        is_active = self.is_active
        is_superuser = self.is_superuser

        return {
            "username": username,
            "password": password,
            "email": email,
            "name": name,
            "is_active": is_active,
            "is_superuser": is_superuser,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> UserCreate:
        username = d["username"]

        password = d["password"]

        email = d.get("email")

        name = d.get("name")

        is_active = d.get("is_active")

        is_superuser = d.get("is_superuser")

        return UserCreate(
            username=username,
            password=password,
            email=email,
            name=name,
            is_active=is_active,
            is_superuser=is_superuser,
        )
