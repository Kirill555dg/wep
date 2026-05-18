import asyncio
import io
import uuid

from app.core import config as core_config
from app.core import minio_client as minio_module
from app.services import exceptions as svc_exc

MAX_FILE_SIZE = 10 * 1024 * 1024

IMAGE_CONTENT_TYPES = frozenset({
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp", "image/x-ms-bmp",
    "audio/mpeg", "audio/wav", "audio/x-wav", "audio/ogg", "audio/mp4", "audio/m4a",
    "video/mp4", "video/webm", "video/quicktime", "video/avi", "video/x-msvideo",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
})
ANSWER_CONTENT_TYPES = frozenset({
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp", "image/x-ms-bmp",
    "audio/mpeg", "audio/wav", "audio/x-wav", "audio/ogg", "audio/mp4", "audio/m4a",
    "video/mp4", "video/webm", "video/quicktime", "video/avi", "video/x-msvideo",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
})

EXT_MAP = {
    "image/jpeg": "jpg", "image/png": "png", "image/gif": "gif", "image/webp": "webp",
    "image/bmp": "bmp", "image/x-ms-bmp": "bmp",
    "audio/mpeg": "mp3", "audio/wav": "wav", "audio/x-wav": "wav", "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/m4a": "m4a",
    "video/mp4": "mp4", "video/webm": "webm", "video/quicktime": "mov", "video/avi": "avi", "video/x-msvideo": "avi",
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}


def _validate(data: bytes, content_type: str, allowed: frozenset) -> str:
    if content_type not in allowed:
        raise svc_exc.ServiceError(f"Unsupported type: {content_type}", code="unsupported_media_type")
    if len(data) > MAX_FILE_SIZE:
        raise svc_exc.ServiceError("File too large (max 10 MB)", code="file_too_large")
    ext = EXT_MAP.get(content_type)
    if not ext:
        raise svc_exc.ServiceError(f"No extension mapping for: {content_type}", code="unsupported_media_type")
    return ext


async def upload_question_image(data: bytes, content_type: str) -> str:
    ext = _validate(data, content_type, IMAGE_CONTENT_TYPES)
    return await _upload(data, content_type, ext)


async def upload_answer_file(data: bytes, content_type: str) -> str:
    ext = _validate(data, content_type, ANSWER_CONTENT_TYPES)
    return await _upload(data, content_type, ext)


async def _upload(data: bytes, content_type: str, ext: str) -> str:
    key = f"{uuid.uuid4().hex}.{ext}"
    bucket = core_config.settings.MINIO_BUCKET
    loop = asyncio.get_running_loop()
    client = minio_module.get_client()

    def _put() -> None:
        minio_module.ensure_bucket()
        client.put_object(
            bucket_name=bucket,
            object_name=key,
            data=io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    await loop.run_in_executor(None, _put)
    return minio_module.public_url(key)
