"""
Database URL helpers.

We keep the settings `DATABASE_URL` as a single source of truth and derive the
correct driver URLs (sync vs async) without string slicing/replacing.
"""

import sqlalchemy.engine as sa_engine


def _render_url(parsed: sa_engine.URL) -> str:
    return parsed.render_as_string(hide_password=False)


def normalize_postgres_url(url: str, *, drivername: str) -> str:
    """Return URL with requested Postgres driver, if URL is PostgreSQL."""
    parsed = sa_engine.make_url(url)
    if parsed.get_backend_name() != "postgresql":
        return _render_url(parsed)
    parsed = parsed.set(drivername=drivername)
    # Async driver doesn't support libpq-specific params (e.g. gssencmode).
    if drivername == "postgresql+asyncpg":
        query = dict(parsed.query)
        query.pop("gssencmode", None)
        parsed = parsed.set(query=query)
    return _render_url(parsed)


def to_psycopg_url(url: str) -> str:
    """Normalize PostgreSQL URL to psycopg3 driver (sync)."""
    return normalize_postgres_url(url, drivername="postgresql+psycopg")


def to_asyncpg_url(url: str) -> str:
    """Normalize PostgreSQL URL to asyncpg driver (async)."""
    return normalize_postgres_url(url, drivername="postgresql+asyncpg")

