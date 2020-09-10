from functools import lru_cache
import secrets
from pydantic import (
    BaseSettings, PostgresDsn
)


class Settings(BaseSettings):
    # jwt token settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # database settings
    DATABASE_URL: PostgresDsn

    # superuser settings
    SU_USERNAME: str
    SU_PASSWORD: str
    SU_EMAIL: str
    SU_NAME: str

    class Config:
        env_file = '.env'


@lru_cache
def get_settings() -> Settings:
    return Settings()
