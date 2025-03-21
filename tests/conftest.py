import asyncio
from unittest.mock import patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.settings import Settings, get_settings
from src.db.tables import Base
from src.main import init_fastapi_app
from src.repos.storage import BaseStorageRepository


class MockStorageRepository(BaseStorageRepository):

    def __init__(self):
        self.storage = {}
        self.ensure_bucket_exists_called = False

    async def get(self, path: str):
        return self.storage.get(path)

    async def put(self, path: str, data: bytes):
        self.storage[path] = data

    async def delete(self, path: str):
        if path in self.storage:
            del self.storage[path]

    async def ensure_bucket_exists(self):
        self.ensure_bucket_exists_called = True


@pytest.fixture(scope="function", autouse=True)
def mock_storage_repository():
    mock_repo = MockStorageRepository()
    with patch("src.repos.storage.create_storage_repository", return_value=mock_repo):
        yield mock_repo


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    settings = get_settings()
    settings.API_TOKEN = "test-api-token"
    settings.DB_NAME = f"{settings.DB_NAME}_test"
    return settings


# FastAPI fixtures
@pytest_asyncio.fixture(scope="session")
async def app(test_settings):
    app = init_fastapi_app()
    app.state.settings = test_settings
    return app


@pytest_asyncio.fixture
async def async_client(app: FastAPI):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def auth_async_client(app: FastAPI, test_settings):
    headers = {"X-API-Token": test_settings.API_TOKEN}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver", headers=headers
    ) as client:
        yield client


def get_db_url(settings: Settings, db_name: str = None) -> str:
    return f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{db_name or settings.DB_NAME}"


async def create_postgres_engine(settings: Settings):
    return create_async_engine(get_db_url(settings, "postgres"), isolation_level="AUTOCOMMIT")


async def terminate_database_connections(conn, database: str):
    """Terminate all connections to the database."""
    await conn.execute(
        text(
            f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database}'
            AND pid <> pg_backend_pid()
            """
        )
    )


@pytest_asyncio.fixture(scope="session")
async def db_engine(test_settings):
    system_engine = None
    test_engine = None

    try:
        system_engine = await create_postgres_engine(test_settings)
        async with system_engine.connect() as conn:
            await terminate_database_connections(conn, test_settings.DB_NAME)
            await conn.execute(text(f"DROP DATABASE IF EXISTS {test_settings.DB_NAME}"))
            await conn.execute(text(f"CREATE DATABASE {test_settings.DB_NAME}"))
        await system_engine.dispose()

        test_engine = create_async_engine(get_db_url(test_settings))
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield test_engine

    finally:
        if test_engine is not None:
            await test_engine.dispose()

        try:
            system_engine = await create_postgres_engine(test_settings)
            async with system_engine.connect() as conn:
                await terminate_database_connections(conn, test_settings.DB_NAME)
                await conn.execute(text(f"DROP DATABASE IF EXISTS {test_settings.DB_NAME}"))
        finally:
            if system_engine is not None:
                await system_engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    factory = sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()
