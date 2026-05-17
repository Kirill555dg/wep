"""
Infrastructure smoke tests.
Verify that PostgreSQL and MinIO are reachable and functional.
These run against the real services, not mocks.
"""

import io
import uuid

import pytest
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio

from app.core import config as core_config
from app.core import minio_client as minio_module

pytestmark = pytest.mark.anyio


# ---------------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------------

async def test_postgres_connect_and_write(db_session: sa_asyncio.AsyncSession) -> None:
    result = await db_session.execute(sa.text("SELECT 1 AS val"))
    assert result.scalar_one() == 1


async def test_postgres_schema_isolation(db_session: sa_asyncio.AsyncSession) -> None:
    """Each db_session fixture gets its own schema; tables exist from metadata."""
    result = await db_session.execute(
        sa.text("SELECT table_name FROM information_schema.tables WHERE table_schema = current_schema()")
    )
    tables = {row[0] for row in result}
    assert "tests" in tables
    assert "questions" in tables
    assert "attempts" in tables
    assert "answers" in tables
    assert "users" in tables


async def test_postgres_insert_and_read(db_session: sa_asyncio.AsyncSession) -> None:
    """Basic CRUD through raw SQL inside the test schema."""
    username = f"u_{uuid.uuid4().hex[:8]}"
    await db_session.execute(
        sa.text(
            "INSERT INTO users (username, email, first_name, last_name, full_name, is_active, created_at, updated_at) "
            "VALUES (:u, :e, 'A', 'B', 'A B', true, now(), now())"
        ),
        {"u": username, "e": f"{username}@test.com"},
    )
    await db_session.commit()

    result = await db_session.execute(sa.text("SELECT email FROM users WHERE username = :u"), {"u": username})
    row = result.scalar_one()
    assert row == f"{username}@test.com"


async def test_postgres_rollback_on_constraint_violation(db_session: sa_asyncio.AsyncSession) -> None:
    """Duplicate email triggers IntegrityError and session recovers after rollback."""
    import sqlalchemy.exc as sa_exc

    email = f"dup_{uuid.uuid4().hex[:8]}@test.com"
    params = {"u1": f"u1_{uuid.uuid4().hex[:6]}", "u2": f"u2_{uuid.uuid4().hex[:6]}", "e": email}

    await db_session.execute(
        sa.text(
            "INSERT INTO users (username, email, first_name, last_name, full_name, is_active, created_at, updated_at) "
            "VALUES (:u1, :e, 'A', 'B', 'A B', true, now(), now())"
        ),
        params,
    )
    await db_session.commit()

    with pytest.raises(sa_exc.IntegrityError):
        await db_session.execute(
            sa.text(
                "INSERT INTO users (username, email, first_name, last_name, full_name, is_active, created_at, updated_at) "
                "VALUES (:u2, :e, 'C', 'D', 'C D', true, now(), now())"
            ),
            params,
        )
        await db_session.commit()

    await db_session.rollback()
    result = await db_session.execute(sa.text("SELECT count(*) FROM users WHERE email = :e"), {"e": email})
    assert result.scalar_one() == 1


# ---------------------------------------------------------------------------
# MinIO / S3
# ---------------------------------------------------------------------------

def _minio_available() -> bool:
    try:
        client = minio_module.get_client()
        client.list_buckets()
        return True
    except Exception:
        return False


requires_minio = pytest.mark.skipif(not _minio_available(), reason="MinIO not reachable")


@requires_minio
async def test_minio_bucket_exists_or_created() -> None:
    minio_module.ensure_bucket()
    client = minio_module.get_client()
    assert client.bucket_exists(core_config.settings.MINIO_BUCKET)


@requires_minio
async def test_minio_upload_and_read() -> None:
    client = minio_module.get_client()
    bucket = core_config.settings.MINIO_BUCKET
    minio_module.ensure_bucket()

    key = f"test/{uuid.uuid4().hex}.txt"
    content = b"hello from integration test"

    client.put_object(bucket, key, io.BytesIO(content), length=len(content), content_type="text/plain")

    response = client.get_object(bucket, key)
    data = response.read()
    response.close()

    assert data == content
    client.remove_object(bucket, key)


@requires_minio
async def test_minio_upload_image_and_url() -> None:
    """Simulate the media upload flow used by question image attachments."""
    from app.services import media_service

    png_1x1 = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    url = await media_service.upload_file(png_1x1, "image/png")

    assert url.startswith("http")
    assert ".png" in url
