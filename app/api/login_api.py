from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas import (Token, UserGet)
from ..deps import (get_db, get_current_user)
from ..services import user_service
from ..config import get_settings
from ..security import create_access_token

router = APIRouter()


@router.post("/access-token", response_model=Token)
async def login_access_token(
        db=Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await user_service.authenticate(
        db, None, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(
        minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {
        "access_token": create_access_token(
            user.uid, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/token-test", response_model=UserGet)
async def test_token(current_user=Depends(get_current_user)):
    """
    Test access token
    """
    return current_user
