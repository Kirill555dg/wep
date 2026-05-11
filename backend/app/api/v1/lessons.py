"""
Lesson management endpoints.
"""

import fastapi
from fastapi import status as http_status

from app.api import dependencies as deps
from app.api import http_errors
from app.api import pagination as api_pagination
from app.models import users as user_models
from app.schemas import pagination as pagination_schemas
from app.schemas import lessons as lesson_schemas
from app.services import exceptions as service_exceptions
from app.services import lesson as lesson_service_module

router = fastapi.APIRouter()


@router.post(
    "",
    response_model=lesson_schemas.LessonResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def create_lesson(
    lesson_data: lesson_schemas.LessonCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    lesson_service: lesson_service_module.LessonService = fastapi.Depends(deps.get_lesson_service),
):
    """Create a new lesson (teachers only, classroom owner only)."""
    try:
        return await lesson_service.create_lesson(lesson_data, current_user.id)
    except service_exceptions.ServiceError as exc:
        status_code = (
            http_status.HTTP_404_NOT_FOUND
            if exc.code == "not_found"
            else http_status.HTTP_403_FORBIDDEN
        )
        raise http_errors.from_service_error(exc, status_code)


@router.get(
    "/classroom/{classroom_id}",
    response_model=pagination_schemas.Page[lesson_schemas.LessonResponse],
)
async def get_classroom_lessons(
    classroom_id: int,
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    lesson_service: lesson_service_module.LessonService = fastapi.Depends(deps.get_lesson_service),
):
    """Return lessons for a classroom.

    Teachers see all lessons (including unpublished); students see only published ones.
    """
    items = await lesson_service.get_classroom_lessons(
        classroom_id, current_user, pagination.skip, pagination.limit,
    )
    total = await lesson_service.count_classroom_lessons(classroom_id, current_user)
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/{lesson_id}", response_model=lesson_schemas.LessonDetailResponse)
async def get_lesson(
    lesson_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    lesson_service: lesson_service_module.LessonService = fastapi.Depends(deps.get_lesson_service),
):
    """Return lesson details by id."""
    lesson = await lesson_service.get_lesson(lesson_id)
    if lesson is None:
        raise http_errors.not_found("Lesson not found")
    return lesson


@router.patch("/{lesson_id}", response_model=lesson_schemas.LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_data: lesson_schemas.LessonUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    lesson_service: lesson_service_module.LessonService = fastapi.Depends(deps.get_lesson_service),
):
    """Update a lesson (classroom owner only)."""
    try:
        result = await lesson_service.update_lesson(lesson_id, lesson_data, current_user.id)
    except service_exceptions.ServiceError as exc:
        status_code = (
            http_status.HTTP_404_NOT_FOUND
            if exc.code == "not_found"
            else http_status.HTTP_403_FORBIDDEN
        )
        raise http_errors.from_service_error(exc, status_code)
    if result is None:
        raise http_errors.not_found("Lesson not found")
    return result


@router.delete("/{lesson_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    lesson_service: lesson_service_module.LessonService = fastapi.Depends(deps.get_lesson_service),
):
    """Delete a lesson (classroom owner only)."""
    try:
        deleted = await lesson_service.delete_lesson(lesson_id, current_user.id)
    except service_exceptions.ServiceError as exc:
        raise http_errors.from_service_error(exc, http_status.HTTP_403_FORBIDDEN)
    if not deleted:
        raise http_errors.not_found("Lesson not found")
    return None
