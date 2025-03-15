from enum import Enum, StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(Enum):
    LOCAL: str = "local"
    DEV: str = "dev"
    PROD: str = "production"


class LogFormat(StrEnum):
    JSON = "json"
    TEXT = "text"


class Settings(BaseSettings):
    APP_NAME: str = "OpenTofu State Manager API"
    APP_DESCRIPTION: str = "OpenTofu State Manager API ..."
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Environment = Field(Environment.LOCAL, alias="ENVIRONMENT")
    ALLOWED_HOSTS: list[str] = Field(["*"], alias="ALLOWED_HOSTS")

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: LogFormat = LogFormat.TEXT

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
