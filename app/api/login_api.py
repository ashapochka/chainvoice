from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas import (Token, UserGet)
from ..deps import get_current_user
from ..services import UserService
from ..config import get_settings
from ..security import create_access_token

router = APIRouter()


@router.post("/access-token/", response_model=Token)
async def login_access_token(
        user_service: UserService = Depends(),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # noinspection PyTypeChecker
    user = await user_service.authenticate(
        None, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(
        minutes=get_settings().access_token_expire_minutes
    )
    return {
        "access_token": create_access_token(
            user.uid, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.get("/me/", response_model=UserGet)
async def me(current_user=Depends(get_current_user)):
    """
    Get authenticated user
    """
    return current_user
