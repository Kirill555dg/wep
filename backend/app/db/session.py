import os
import typing as tp

import sqlalchemy.ext.asyncio as sa_asyncio
import sqlalchemy.orm as sqla_orm
import sqlalchemy.pool as sa_pool

from app.core import config as core_config
from app.db import url as db_url

SYNC_DATABASE_URL = db_url.to_psycopg_url(core_config.settings.DATABASE_URL)
ASYNC_DATABASE_URL = db_url.to_asyncpg_url(core_config.settings.DATABASE_URL)

_testing = os.environ.get("TESTING") == "1"

if _testing:
    async_engine = sa_asyncio.create_async_engine(ASYNC_DATABASE_URL, echo=False, poolclass=sa_pool.NullPool)
else:
    async_engine = sa_asyncio.create_async_engine(
        ASYNC_DATABASE_URL, echo=core_config.settings.DEBUG, pool_pre_ping=True, pool_size=5, max_overflow=10
    )

AsyncSessionLocal = sa_asyncio.async_sessionmaker(
    bind=async_engine, autocommit=False, autoflush=False, expire_on_commit=False
)

Base = sqla_orm.declarative_base()


async def get_db() -> tp.AsyncGenerator[sa_asyncio.AsyncSession, None]:
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
