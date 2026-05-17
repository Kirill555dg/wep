import typing as tp
from datetime import timedelta

import minio

from app.core import config as core_config

_client: minio.Minio | None = None


def get_client() -> minio.Minio:
    global _client
    if _client is None:
        _client = minio.Minio(
            endpoint=core_config.settings.MINIO_ENDPOINT,
            access_key=core_config.settings.MINIO_ACCESS_KEY,
            secret_key=core_config.settings.MINIO_SECRET_KEY,
            secure=core_config.settings.MINIO_SECURE,
        )
    return _client


def ensure_bucket() -> None:
    client = get_client()
    bucket = core_config.settings.MINIO_BUCKET
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def presigned_get_url(object_name: str, expires_seconds: int = 3600) -> str:
    client = get_client()
    bucket = core_config.settings.MINIO_BUCKET
    url = client.presigned_get_object(bucket, object_name, expires=timedelta(seconds=expires_seconds))
    return tp.cast(str, url)
