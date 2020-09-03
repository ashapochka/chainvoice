from databases import Database
from sqlalchemy import (
    MetaData,
    Table, Column,
    Integer, String, Boolean,
    create_engine
)
from .config import get_settings


database = Database(get_settings().database_url)
metadata = MetaData()


notes = Table(
    "notes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("text", String),
    Column("completed", Boolean),
)


engine = create_engine(
    get_settings().database_url, pool_size=3, max_overflow=0
)


def create_schema():
    metadata.create_all(engine)


async def connect_databases():
    await database.connect()


async def disconnect_databases():
    await database.disconnect()
