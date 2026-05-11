"""
Homework management endpoints.
"""

import fastapi
from fastapi import status as http_status

from app.api import dependencies as deps
from app.api import http_errors
from app.api import pagination as api_pagination
from app.models import users as user_models
from app.schemas import pagination as pagination_schemas
from app.schemas import homework as homework_schemas
from app.services import exceptions as service_exceptions
from app.services import homework as homework_service_module

router = fastapi.APIRouter()


@router.post(
    "",
    response_model=homework_schemas.HomeworkResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def create_homework(
    homework_data: homework_schemas.HomeworkCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    homework_service: homework_service_module.HomeworkService = fastapi.Depends(
        deps.get_homework_service
    ),
):
    """Create a new homework assignment (classroom owner only)."""
    try:
        return await homework_service.create_homework(homework_data, current_user.id)
    except service_exceptions.ServiceError as exc:
        status_code = (
            http_status.HTTP_404_NOT_FOUND
            if exc.code in ("lesson_not_found", "not_found")
            else http_status.HTTP_403_FORBIDDEN
        )
        raise http_errors.from_service_error(exc, status_code)


@router.get(
    "/lesson/{lesson_id}",
    response_model=pagination_schemas.Page[homework_schemas.HomeworkResponse],
)
async def get_lesson_homework(
    lesson_id: int,
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    homework_service: homework_service_module.HomeworkService = fastapi.Depends(
        deps.get_homework_service
    ),
):
    """Return homework for a lesson.

    Teachers see all homework; students see only published homework.
    """
    items = await homework_service.get_lesson_homework(
        lesson_id, current_user, pagination.skip, pagination.limit,
    )
    total = await homework_service.count_lesson_homework(lesson_id, current_user)
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/{homework_id}", response_model=homework_schemas.HomeworkDetailResponse)
async def get_homework(
    homework_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    homework_service: homework_service_module.HomeworkService = fastapi.Depends(
        deps.get_homework_service
    ),
):
    """Return homework details; students can only see published homework."""
    try:
        result = await homework_service.get_homework(homework_id, current_user)
    except service_exceptions.ServiceError as exc:
        if exc.code == "unpublished":
            raise http_errors.forbidden(exc.message, code=exc.code)
        raise
    if result is None:
        raise http_errors.not_found("Homework not found")
    return result


@router.get(
    "/{homework_id}/problems",
    response_model=list[homework_schemas.ProblemResponse | homework_schemas.ProblemFullResponse],
)
async def get_homework_problems(
    homework_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    homework_service: homework_service_module.HomeworkService = fastapi.Depends(
        deps.get_homework_service
    ),
):
    """Return problems for a homework.

    Teachers see the full problem including correct answers; students see the limited view.
    """
    result = await homework_service.get_homework_problems(homework_id, current_user)
    if result is None:
        raise http_errors.not_found("Homework not found")
    return result


@router.patch("/{homework_id}", response_model=homework_schemas.HomeworkResponse)
async def update_homework(
    homework_id: int,
    homework_data: homework_schemas.HomeworkUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    homework_service: homework_service_module.HomeworkService = fastapi.Depends(
        deps.get_homework_service
    ),
):
    """Update homework (classroom owner only)."""
    try:
        result = await homework_service.update_homework(homework_id, homework_data, current_user.id)
    except service_exceptions.ServiceError as exc:
        raise http_errors.from_service_error(exc, http_status.HTTP_403_FORBIDDEN)
    if result is None:
        raise http_errors.not_found("Homework not found")
    return result


@router.delete("/{homework_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_homework(
    homework_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    homework_service: homework_service_module.HomeworkService = fastapi.Depends(
        deps.get_homework_service
    ),
):
    """Delete homework (classroom owner only). Not yet implemented."""
    return None
