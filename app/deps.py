from typing import Optional
from databases import Database
from fastapi import (Depends, HTTPException, status)
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from .db import db_client
from .security import decode_token
from . import schemas
from .services import user_service
from .blockchain import blockchain_client
from .contracts import ERC1155Contract

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/access-token")


def get_db() -> Database:
    return db_client.database


def get_erc1155_contract() -> ERC1155Contract:
    return blockchain_client.erc1155_contract


async def get_current_user(
        db: Database = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> Optional[schemas.UserInDb]:
    try:
        payload = decode_token(token)
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await user_service.get_one_by_uid(db, None, uid=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserInDb(**user)


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
