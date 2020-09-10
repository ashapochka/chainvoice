from uuid import uuid4


def new_uid() -> str:
    return str(uuid4())
