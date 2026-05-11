"""
Statistics and results endpoints.
"""

import fastapi

from app.api import dependencies as deps
from app.api import http_errors
from app.api import pagination as api_pagination
from app.models import users as user_models
from app.schemas import pagination as pagination_schemas
from app.schemas import homework as homework_schemas
from app.schemas import progress as progress_schemas
from app.services import result as result_service_module

router = fastapi.APIRouter()


@router.get("/me", response_model=pagination_schemas.Page[homework_schemas.StatisticsResponse])
async def get_my_statistics(
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_student),
    result_service: result_service_module.ResultService = fastapi.Depends(deps.get_result_service),
):
    """Return all homework attempt statistics for the current student."""
    items = await result_service.get_student_statistics(current_user.id, pagination.skip, pagination.limit)
    total = await result_service.count_student_statistics(current_user.id)
    if items is None or total is None:
        raise http_errors.not_found("Student profile not found")
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/me/progress", response_model=progress_schemas.StudentProgressResponse)
async def get_my_progress(
    current_user: user_models.User = fastapi.Depends(deps.get_current_student),
    result_service: result_service_module.ResultService = fastapi.Depends(deps.get_result_service),
):
    """Return overall progress summary for the current student."""
    result = await result_service.get_student_progress(current_user.id)
    if result is None:
        raise http_errors.not_found("Student profile not found")
    return result


@router.get(
    "/homework/{homework_id}",
    response_model=pagination_schemas.Page[homework_schemas.StatisticsResponse],
)
async def get_homework_statistics(
    homework_id: int,
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    result_service: result_service_module.ResultService = fastapi.Depends(deps.get_result_service),
):
    """Return attempt statistics for all students on a specific homework (teachers only)."""
    items = await result_service.get_homework_statistics(
        homework_id, current_user.id, pagination.skip, pagination.limit,
    )
    total = await result_service.count_homework_statistics(homework_id)
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get(
    "/classroom/{classroom_id}/progress",
    response_model=progress_schemas.ClassroomProgressResponse,
)
async def get_classroom_progress(
    classroom_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    result_service: result_service_module.ResultService = fastapi.Depends(deps.get_result_service),
):
    """Return progress summary for a classroom (teachers only)."""
    return await result_service.get_classroom_progress(classroom_id, current_user.id)


@router.get(
    "/student/{student_user_id}",
    response_model=pagination_schemas.Page[homework_schemas.StatisticsResponse],
)
async def get_student_statistics_by_teacher(
    student_user_id: int,
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    result_service: result_service_module.ResultService = fastapi.Depends(deps.get_result_service),
):
    """Return statistics for a specific student (teachers only)."""
    items = await result_service.get_student_statistics(student_user_id, pagination.skip, pagination.limit)
    total = await result_service.count_student_statistics(student_user_id)
    if items is None or total is None:
        raise http_errors.not_found("Student not found")
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)
