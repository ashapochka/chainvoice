from uuid import uuid4
from datetime import datetime


def new_uid() -> str:
    return str(uuid4())


def current_time() -> datetime:
    return datetime.now()
