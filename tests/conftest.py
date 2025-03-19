import asyncio

import asyncpg
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.settings import get_settings
from src.db.models import Base
from src.main import init_fastapi_app

settings = get_settings()


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
def app():
    app = init_fastapi_app()
    return app


@pytest_asyncio.fixture
async def async_client(app: FastAPI):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def db_engine():
    async def get_postgres_connection():
        return await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USERNAME,
            password=settings.DB_PASSWORD,
            database="postgres",
        )

    test_db_name = f"{settings.DB_NAME}_test"
    conn = await get_postgres_connection()

    await conn.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    await conn.execute(f"CREATE DATABASE {test_db_name}")
    await conn.close()

    test_engine = create_async_engine(
        f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{test_db_name}"
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    await test_engine.dispose()

    conn = await get_postgres_connection()

    await conn.execute(
        f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{test_db_name}'
        AND pid <> pg_backend_pid()
    """
    )
    await conn.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    await conn.close()


@pytest_asyncio.fixture
async def db_session(db_engine):
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()
