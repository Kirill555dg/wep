"""
Database session management
"""

import typing as tp

from sqlalchemy import orm as orm
from sqlalchemy.ext import asyncio as sa_asyncio

from app.core import config as core_config
from app.db import url as db_url

# Derive async/sync URLs from settings (no string replacements).
SYNC_DATABASE_URL = db_url.to_psycopg_url(core_config.settings.DATABASE_URL)
ASYNC_DATABASE_URL = db_url.to_asyncpg_url(core_config.settings.DATABASE_URL)

async_engine = sa_asyncio.create_async_engine(
    ASYNC_DATABASE_URL,
    echo=core_config.settings.DEBUG,
    pool_pre_ping=True,  # Проверять соединения перед использованием
    pool_size=5,  # Размер пула соединений
    max_overflow=10,  # Максимальное количество дополнительных соединений
)

# Create SessionLocal class
AsyncSessionLocal = sa_asyncio.async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Create Base class for declarative models
Base = orm.declarative_base()


async def get_db() -> tp.AsyncGenerator[sa_asyncio.AsyncSession, None]:
    """
    Dependency for getting database session

    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
