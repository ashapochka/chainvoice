from typing import Optional
from pydantic import EmailStr, SecretStr
from .base import (BaseSchema, UIDSchema)


# Shared properties
class UserBase(BaseSchema):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = False
    is_superuser: bool = False
    is_anonymous: Optional[bool] = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    password: SecretStr


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[SecretStr] = None


class UserGet(UserBase, UIDSchema):
    pass


class UserInDb(UserGet):
    id: int
    hashed_password: Optional[str] = None
