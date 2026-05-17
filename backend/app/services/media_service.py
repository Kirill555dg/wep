import asyncio
import io
import uuid

from app.core import config as core_config
from app.core import minio_client as minio_module
from app.services import exceptions as svc_exc

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/gif", "image/webp"})
EXT_MAP = {"image/jpeg": "jpg", "image/png": "png", "image/gif": "gif", "image/webp": "webp"}


async def upload_file(data: bytes, content_type: str) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise svc_exc.ServiceError(f"Unsupported type: {content_type}", code="unsupported_media_type")
    if len(data) > MAX_FILE_SIZE:
        raise svc_exc.ServiceError("File too large (max 10 MB)", code="file_too_large")

    key = f"{uuid.uuid4().hex}.{EXT_MAP[content_type]}"
    bucket = core_config.settings.MINIO_BUCKET
    loop = asyncio.get_running_loop()
    client = minio_module.get_client()

    def _upload() -> None:
        minio_module.ensure_bucket()
        client.put_object(
            bucket_name=bucket,
            object_name=key,
            data=io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    await loop.run_in_executor(None, _upload)
    return minio_module.presigned_get_url(key)
