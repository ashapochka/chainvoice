from functools import lru_cache
import secrets
from pydantic import (
    BaseSettings, PostgresDsn
)
from fastapi_utils.api_settings import APISettings


class Settings(APISettings):
    # jwt token settings
    secret_key: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    access_token_expire_minutes: int = 60 * 24 * 8

    # database settings
    database_url: PostgresDsn

    # superuser settings
    su_username: str
    su_password: str
    su_email: str
    su_name: str

    class Config:
        env_prefix = 'chainvoice_'
        env_file = '.env'


@lru_cache
def get_settings() -> Settings:
    return Settings()
