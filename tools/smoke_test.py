#!/usr/bin/env python3
"""
Production smoke test — verifies infrastructure connectivity.

Reads configuration from environment variables; falls back to defaults for
local development. Uses only packages from requirements.txt (no dev deps).

Usage:
    python tools/smoke_test.py
    DATABASE_URL=postgresql://... MINIO_ENDPOINT=... python tools/smoke_test.py

Exit codes:
    0 — all checks passed
    1 — one or more checks failed
"""

import os
import sys
import urllib.request


def _env(key: str, default: str) -> str:
    return os.environ.get(key, default)


def check_postgres() -> bool:
    import psycopg  # type: ignore[import]

    url = _env("DATABASE_URL", "postgresql://wep_user:wep_password@localhost:5433/wep_education")
    try:
        with psycopg.connect(url) as conn:
            row = conn.execute("SELECT current_schema()").fetchone()
            schema = row[0] if row else "?"
        print(f"  [ok] PostgreSQL  schema={schema}")
        return True
    except Exception as exc:
        print(f"  [FAIL] PostgreSQL  {exc}")
        return False


def check_minio() -> bool:
    import minio  # type: ignore[import]

    endpoint = _env("MINIO_ENDPOINT", "127.0.0.1:9000")
    access_key = _env("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = _env("MINIO_SECRET_KEY", "minioadmin")
    secure = _env("MINIO_SECURE", "false").lower() == "true"
    try:
        client = minio.Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
        buckets = [b.name for b in client.list_buckets()]
        print(f"  [ok] MinIO  buckets={buckets}")
        return True
    except Exception as exc:
        print(f"  [FAIL] MinIO  {exc}")
        return False


def check_api() -> bool:
    import json

    url = _env("API_URL", "http://localhost:8023")
    try:
        with urllib.request.urlopen(f"{url}/", timeout=5) as resp:
            data = json.loads(resp.read())
        print(f"  [ok] API  version={data.get('version', '?')}")
        return True
    except Exception as exc:
        print(f"  [FAIL] API  {exc}")
        return False


def check_migrations() -> bool:
    """Verify that the latest Alembic revision is applied."""
    import psycopg  # type: ignore[import]

    url = _env("DATABASE_URL", "postgresql://wep_user:wep_password@localhost:5433/wep_education")
    try:
        with psycopg.connect(url) as conn:
            row = conn.execute(
                "SELECT version_num FROM alembic_version LIMIT 1"
            ).fetchone()
        rev = row[0] if row else None
        print(f"  [ok] Migrations  revision={rev}")
        return True
    except Exception as exc:
        print(f"  [FAIL] Migrations  {exc}")
        return False


CHECKS = [
    ("PostgreSQL", check_postgres),
    ("MinIO", check_minio),
    ("Migrations", check_migrations),
    ("API", check_api),
]


def main() -> int:
    print("smoke_test: checking infrastructure...\n")
    results = []
    for name, fn in CHECKS:
        print(f"[{name}]")
        ok = fn()
        results.append(ok)
        print()

    passed = sum(results)
    total = len(results)
    status = "ALL OK" if passed == total else f"{total - passed} FAILED"
    print(f"Result: {passed}/{total} checks passed — {status}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
