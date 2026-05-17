import os
import typing as tp
import uuid

import httpx
import pytest
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio

from app import models as _models  # noqa: F401 — registers ORM metadata
from app.core import config as core_config
from app.db import session as db_session_module
from app.db import url as db_url

pytest_plugins = ("anyio",)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


def _make_schema_name() -> str:
    return f"test_{uuid.uuid4().hex}"


async def _create_schema(sync_url: str, async_url: str, schema: str) -> sa_asyncio.AsyncEngine:
    """Create schema and tables; return the async engine."""
    admin_engine = sa.create_engine(sync_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(sa.text(f'CREATE SCHEMA "{schema}"'))
    admin_engine.dispose()

    engine = sa_asyncio.create_async_engine(
        async_url, connect_args={"server_settings": {"search_path": schema}}, pool_pre_ping=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(db_session_module.Base.metadata.create_all)
    return engine


def _drop_schema(sync_url: str, schema: str) -> None:
    admin_engine = sa.create_engine(sync_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(sa.text(f'DROP SCHEMA "{schema}" CASCADE'))
    admin_engine.dispose()


@pytest.fixture(scope="function")
async def db_session() -> tp.AsyncGenerator[sa_asyncio.AsyncSession, None]:
    """
    Fresh PostgreSQL schema per test function.
    Yields a single AsyncSession for direct service-layer testing.
    Schema is dropped on teardown.
    """
    database_url = os.environ.get("DATABASE_URL", core_config.settings.DATABASE_URL)
    sync_url = db_url.to_psycopg_url(database_url)
    async_url = db_url.to_asyncpg_url(database_url)
    schema = _make_schema_name()

    engine = await _create_schema(sync_url, async_url, schema)
    session_factory = sa_asyncio.async_sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    try:
        async with session_factory() as session:
            yield session
    finally:
        await engine.dispose()
        _drop_schema(sync_url, schema)


@pytest.fixture(scope="function")
async def http_client() -> tp.AsyncGenerator[httpx.AsyncClient, None]:
    """
    Async HTTP client backed by an isolated test schema.
    Each HTTP request gets its own session so a failed transaction
    in one request does not poison subsequent requests.
    Schema is dropped after the test function completes.
    """
    from app.main import app

    database_url = os.environ.get("DATABASE_URL", core_config.settings.DATABASE_URL)
    sync_url = db_url.to_psycopg_url(database_url)
    async_url = db_url.to_asyncpg_url(database_url)
    schema = _make_schema_name()

    engine = await _create_schema(sync_url, async_url, schema)
    session_factory = sa_asyncio.async_sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )

    async def _override_get_db() -> tp.AsyncGenerator[sa_asyncio.AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[db_session_module.get_db] = _override_get_db
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.pop(db_session_module.get_db, None)
        await engine.dispose()
        _drop_schema(sync_url, schema)
