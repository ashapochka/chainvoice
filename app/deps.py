from databases import Database
from .db import database


def get_db() -> Database:
    return database
