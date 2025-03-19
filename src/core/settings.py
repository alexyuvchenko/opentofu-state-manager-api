from enum import Enum, StrEnum
from functools import lru_cache

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
    APP_NAME: str = Field("OpenTofu State Manager API", alias="APP_NAME")
    APP_DESCRIPTION: str = Field("API for managing OpenTofu state", alias="APP_DESCRIPTION")
    APP_VERSION: str = Field("0.1.0", alias="APP_VERSION")
    ENVIRONMENT: Environment = Field(Environment.LOCAL, alias="ENVIRONMENT")
    ALLOWED_HOSTS: list[str] = Field(["*"], alias="ALLOWED_HOSTS")
    LOG_LEVEL: str = Field("INFO", alias="LOG_LEVEL")
    LOG_FORMAT: LogFormat = Field(LogFormat.TEXT, alias="LOG_FORMAT")
    DB_ECHO: bool = Field(False, alias="DB_ECHO")
    API_TOKEN: str = Field("API_TOKEN=managing-opentofu-state-secure-api-token", alias="API_TOKEN")

    DB_USERNAME: str = Field("postgres", alias="DB_USERNAME")
    DB_PASSWORD: str = Field("opentofu", alias="DB_PASSWORD")
    DB_HOST: str = Field("localhost", alias="DB_HOST")
    DB_PORT: str = Field("5432", alias="DB_PORT")
    DB_NAME: str = Field("opentofu_state", alias="DB_NAME")

    MINIO_ENDPOINT: str = Field("localhost:9000", alias="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field("minioadmin", alias="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field("minioadmin", alias="MINIO_SECRET_KEY")
    MINIO_SECURE: bool = Field(False, alias="MINIO_SECURE")
    MINIO_BUCKET_NAME: str = Field("opentofu-states", alias="MINIO_BUCKET_NAME")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
