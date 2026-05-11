"""Pytest configuration and fixtures."""

import os
import typing as tp
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy import orm as orm
from sqlalchemy.ext import asyncio as sa_asyncio

from app import models as _models  # noqa: F401
from app.core import config as core_config
from app.db import session as db_session_module
from app.db import url as db_url


@pytest.fixture(scope="function")
async def db_session() -> tp.AsyncIterator[sa_asyncio.AsyncSession]:
    """Create a fresh PostgreSQL schema for each test."""
    database_url = os.environ.get("DATABASE_URL", core_config.settings.DATABASE_URL)
    sync_url = db_url.to_psycopg_url(database_url)
    async_url = db_url.to_asyncpg_url(database_url)

    schema = f"test_{uuid.uuid4().hex}"
    admin_engine = sa.create_engine(sync_url, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(sa.text(f'CREATE SCHEMA "{schema}"'))

    engine = sa_asyncio.create_async_engine(
        async_url,
        connect_args={"server_settings": {"search_path": schema}},
        pool_pre_ping=True,
    )
    async with engine.begin() as connection:
        await connection.run_sync(db_session_module.Base.metadata.create_all)

    try:
        session_local = sa_asyncio.async_sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
        async with session_local() as session:
            yield session
    finally:
        await engine.dispose()
        with admin_engine.connect() as connection:
            connection.execute(sa.text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin_engine.dispose()


def mypy_config_resource() -> tuple[str, str]:
    """Provide mypy config location for plugins."""
    return "backend", "backend/mypy.ini"


def mypy_check_root() -> str:
    """Root directory to type-check."""
    return "backend"
