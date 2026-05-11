"""
Lesson management endpoints
"""

import fastapi
from fastapi import status as http_status

from app.api import dependencies as deps
from app.api import pagination as api_pagination
from app.models import users as user_models
from app.schemas import pagination as pagination_schemas
from app.schemas import lessons as lesson_schemas
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
    """
    Create new lesson (teachers only)

    - **classroom_id**: ID of the classroom
    - **title**: Lesson title
    - **description**: Optional description
    - **scheduled_at**: Optional scheduled date/time
    - **theory_material_ids**: List of theory material IDs to attach
    """
    return await lesson_service.create_lesson(lesson_data, current_user.id)


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
    """
    Get all lessons for a classroom

    - Teachers see all lessons (including unpublished)
    - Students see only published lessons
    """
    items = await lesson_service.get_classroom_lessons(
        classroom_id, current_user, pagination.skip, pagination.limit
    )
    total = await lesson_service.count_classroom_lessons(classroom_id, current_user)
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/{lesson_id}", response_model=lesson_schemas.LessonDetailResponse)
async def get_lesson(
    lesson_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    lesson_service: lesson_service_module.LessonService = fastapi.Depends(deps.get_lesson_service),
):
    """
    Get lesson details by ID
    """
    return await lesson_service.get_lesson(lesson_id)


@router.patch("/{lesson_id}", response_model=lesson_schemas.LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_data: lesson_schemas.LessonUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    lesson_service: lesson_service_module.LessonService = fastapi.Depends(deps.get_lesson_service),
):
    """
    Update lesson (teachers only, owner only)
    """
    return await lesson_service.update_lesson(lesson_id, lesson_data, current_user.id)


@router.delete("/{lesson_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    lesson_service: lesson_service_module.LessonService = fastapi.Depends(deps.get_lesson_service),
):
    """
    Delete lesson (teachers only, owner only)
    """
    await lesson_service.delete_lesson(lesson_id, current_user.id)
    return None
