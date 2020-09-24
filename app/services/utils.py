from uuid import uuid4
from datetime import datetime

from fastapi import (HTTPException, status)


def new_uid() -> str:
    return str(uuid4())


def current_time() -> datetime:
    return datetime.now()


def raise_4xx(status_code, detail):
    raise HTTPException(
        status_code=status_code,
        detail=detail
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
