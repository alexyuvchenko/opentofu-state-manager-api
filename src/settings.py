from enum import Enum, StrEnum
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(Enum):
    LOCAL: str = "local"
    DEV: str = "dev"
    PROD: str = "prod"


class LogFormat(StrEnum):
    JSON = "json"
    TEXT = "text"


class Settings(BaseSettings):
    APP_NAME: str = "OpenTofu State Manager API"
    APP_DESCRIPTION: str = "API for managing OpenTofu state"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Environment = Field(Environment.LOCAL, alias="ENVIRONMENT")
    ALLOWED_HOSTS: list[str] = Field(["*"], alias="ALLOWED_HOSTS")

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: LogFormat = LogFormat.TEXT

    # Database settings
    DATABASE_URL: str = (
        "postgresql+asyncpg://opentofu:opentofu@localhost:5432/opentofu_state_manager"
    )
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # MinIO settings
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "opentofu-states"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
