"""
Infrastructure health checker.

Reads configuration from environment variables or CLI flags.

Usage:
    uv run python -m health_checker
    uv run python -m health_checker --database-url postgresql://...
    health-checker                              # after build or uv tool install

Exit codes:
    0  — all checks passed
    1  — one or more checks failed
"""

import logging
import json
import urllib.request

import click

import minio
import psycopg

LOGGER = logging.getLogger(__name__)

DATABASE_URL = "postgresql://wep_user:wep_password@localhost:5433/wep_education"
MINIO_ENDPOINT = "127.0.0.1:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
API_URL = "http://localhost:8023"


def check_postgres(database_url: str) -> bool:
    """Check PostgreSQL connectivity."""
    try:
        with psycopg.connect(database_url) as conn:
            row = conn.execute("SELECT current_schema()").fetchone()
            schema = row[0] if row else "?"
        LOGGER.info(f"  [ok] PostgreSQL  schema=`{schema}`")
        return True
    except Exception as exc:
        LOGGER.error(f"  [FAIL] PostgreSQL  {exc}")
        return False


def check_minio(endpoint: str, access_key: str, secret_key: str, secure: bool) -> bool:
    """Check MinIO connectivity."""
    try:
        client = minio.Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
        buckets = [b.name for b in client.list_buckets()]
        LOGGER.info(f"  [ok] MinIO  buckets=`{buckets}`")
        return True
    except Exception as exc:
        LOGGER.error(f"  [FAIL] MinIO  {exc}")
        return False


def check_migrations(database_url: str) -> bool:
    """Verify that Alembic migrations are applied."""
    try:
        with psycopg.connect(database_url) as conn:
            row = conn.execute(
                "SELECT version_num FROM alembic_version LIMIT 1"
            ).fetchone()
        rev = row[0] if row else None
        LOGGER.info(f"  [ok] Migrations  revision=`{rev}`")
        return True
    except Exception as exc:
        LOGGER.error(f"  [FAIL] Migrations  {exc}")
        return False


def check_api(api_url: str) -> bool:
    """Check API health endpoint."""
    try:
        with urllib.request.urlopen(f"{api_url}/", timeout=5) as resp:
            data = json.loads(resp.read())
        version = data.get("version", "?")
        LOGGER.info(f"  [ok] API  version=`{version}`")
        return True
    except Exception as exc:
        LOGGER.error(f"  [FAIL] API  {exc}")
        return False


@click.command()
@click.option("--database-url", envvar="DATABASE_URL", default=DATABASE_URL)
@click.option("--minio-endpoint", envvar="MINIO_ENDPOINT", default=MINIO_ENDPOINT)
@click.option("--minio-access-key", envvar="MINIO_ACCESS_KEY", default=MINIO_ACCESS_KEY)
@click.option("--minio-secret-key", envvar="MINIO_SECRET_KEY", default=MINIO_SECRET_KEY)
@click.option("--minio-secure", envvar="MINIO_SECURE", is_flag=True)
@click.option("--api-url", envvar="API_URL", default=API_URL)
@click.option("--verbose", "-v", is_flag=True)
def main(
    database_url: str,
    minio_endpoint: str,
    minio_access_key: str,
    minio_secret_key: str,
    minio_secure: bool,
    api_url: str,
    verbose: bool,
) -> int:
    """Check infrastructure components."""
    fmt = "%(message)s"
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(format=fmt, level=level)

    LOGGER.info("health_checker: checking infrastructure...")
    LOGGER.info("")

    passed = 0
    total = 0

    checks = [
        ("PostgreSQL", lambda: check_postgres(database_url)),
        ("MinIO", lambda: check_minio(minio_endpoint, minio_access_key, minio_secret_key, minio_secure)),
        ("Migrations", lambda: check_migrations(database_url)),
        ("API", lambda: check_api(api_url)),
    ]

    for name, fn in checks:
        total += 1
        LOGGER.warning(f"[{name}]")
        if fn():
            passed += 1
        LOGGER.info("")

    status = "ALL OK" if passed == total else f"{total - passed} FAILED"
    LOGGER.warning(f"Result: {passed}/{total} checks passed -- {status}")

    LOGGER.debug("Shutting down...")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
