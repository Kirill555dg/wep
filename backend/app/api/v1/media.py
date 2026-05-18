"""
Media API: file upload for question images and answer files.
"""

import fastapi
from fastapi import status as http_status

from app.api import dependencies as deps
from app.api import http_errors
from app.models import users as user_models
from app.services import exceptions as service_exceptions
from app.services import media_service

router = fastapi.APIRouter()


@router.post("/upload", status_code=http_status.HTTP_201_CREATED)
async def upload_media(
    file: fastapi.UploadFile = fastapi.File(...),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
) -> dict[str, str]:
    data = await file.read()
    try:
        url = await media_service.upload_question_image(data, file.content_type)
    except service_exceptions.ServiceError as exc:
        if exc.code == "file_too_large":
            raise http_errors.bad_request(exc.message, code=exc.code)
        if exc.code == "unsupported_media_type":
            raise http_errors.bad_request(exc.message, code=exc.code)
        raise

    return {"url": url}


@router.post("/upload-answer", status_code=http_status.HTTP_201_CREATED)
async def upload_answer_file(
    file: fastapi.UploadFile = fastapi.File(...),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
) -> dict[str, str]:
    data = await file.read()
    try:
        url = await media_service.upload_answer_file(data, file.content_type)
    except service_exceptions.ServiceError as exc:
        if exc.code == "file_too_large":
            raise http_errors.bad_request(exc.message, code=exc.code)
        if exc.code == "unsupported_media_type":
            raise http_errors.bad_request(exc.message, code=exc.code)
        raise

    return {"url": url}
