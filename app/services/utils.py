from decimal import Decimal
from uuid import uuid4
from datetime import datetime

from fastapi import (HTTPException, status)

from app.schemas import UserInDb


def new_uid() -> str:
    return str(uuid4())


def current_time() -> datetime:
    return datetime.now()


def raise_4xx(status_code, detail, headers=None):
    raise HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers
    )


def raise_not_authenticated():
    raise_4xx(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_unauthorized():
    raise_4xx(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized for operation",
    )


def raise_not_found(what, by, msg='object not found'):
    raise_4xx(
        status.HTTP_404_NOT_FOUND,
        detail={
            'what': str(what),
            'by': str(by),
            'msg': msg
        }
    )


def raise_not_found_if_none(obj, what, by, msg=None):
    if not msg:
        msg = 'object not found'
    if obj is None:
        raise_not_found(what, by, msg=msg)


def raise_forbidden(msg='action forbidden', **kwargs):
    raise_4xx(
        status.HTTP_403_FORBIDDEN,
        detail={
            'msg': msg,
            **kwargs
        }
    )


def to_money(amount) -> Decimal:
    if not isinstance(amount, Decimal):
        amount = Decimal(amount)
    return round(amount, ndigits=2)


def money_to_token(money_amount) -> int:
    return int(round(money_amount * 100))


def token_to_money(token_amount: int) -> Decimal:
    return round(Decimal(token_amount) / 100, ndigits=2)


def ensure_authenticated(user: UserInDb):
    if not user or not user.is_active or user.is_anonymous:
        raise_not_authenticated()


def ensure_superuser(user: UserInDb):
    ensure_authenticated(user)
    if not user.is_superuser:
        raise_unauthorized()
