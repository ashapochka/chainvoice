from typing import Optional
from uuid import UUID, uuid4

from databases import Database
from fastapi import (Depends, HTTPException, status)
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from .db import get_db
from .security import decode_token
from . import schemas
from .services import UserService


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/login/access-token/",
    auto_error=False
)


anonymous_user = schemas.UserInDb(
    uid=uuid4(),
    id=-1,
    is_anonymous=True,
    is_active=True,
    is_superuser=False
)


async def get_current_user(
        db: Database = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> Optional[schemas.UserInDb]:
    if token:
        try:
            payload = decode_token(token)
            token_data = schemas.TokenPayload(**payload)
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user = await UserService(db).get_one_by_uid(
            None, uid=UUID(token_data.sub)
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return schemas.UserInDb(**user)
    else:
        return anonymous_user


def get_current_active_user(
        current_user: schemas.UserInDb = Depends(get_current_user),
) -> Optional[schemas.UserInDb]:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
        current_user: schemas.UserInDb = Depends(get_current_user),
) -> Optional[schemas.UserInDb]:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
