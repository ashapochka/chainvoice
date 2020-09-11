from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class UserUpdate:
    """ Intended for use as a base class for externally-facing models.

Any models that inherit from this class will:
* accept fields using snake_case or camelCase keys
* use camelCase keys in the generated OpenAPI spec
* have orm_mode on by default
    * Because of this, FastAPI will automatically attempt to parse returned orm instances into the model """

    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False
    password: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        username = self.username
        email = self.email
        name = self.name
        is_active = self.is_active
        is_superuser = self.is_superuser
        password = self.password

        return {
            "username": username,
            "email": email,
            "name": name,
            "isActive": is_active,
            "isSuperuser": is_superuser,
            "password": password,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> UserUpdate:
        username = d.get("username")

        email = d.get("email")

        name = d.get("name")

        is_active = d.get("isActive")

        is_superuser = d.get("isSuperuser")

        password = d.get("password")

        return UserUpdate(
            username=username,
            email=email,
            name=name,
            is_active=is_active,
            is_superuser=is_superuser,
            password=password,
        )
