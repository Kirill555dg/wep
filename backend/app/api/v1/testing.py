"""
Testing/answer-submission endpoints.
"""

import typing as tp

import fastapi
from fastapi import status as http_status
from sqlalchemy.ext import asyncio as sa_asyncio

from app.api import dependencies as deps
from app.api import http_errors
from app.core import config as core_config
from app.db import session as db_session
from app.repositories import classroom as classroom_repository
from app.repositories import user as user_repository
from app.models import users as user_models
from app.schemas import homework as homework_schemas
from app.services import exceptions as service_exceptions
from app.services import testing as testing_service_module

router = fastapi.APIRouter()


@router.post("/submit-answer", response_model=homework_schemas.StatisticsResponse)
async def submit_answer(
    answer_data: homework_schemas.AnswerSubmit,
    current_user: user_models.User = fastapi.Depends(deps.get_current_student),
    testing_service: testing_service_module.TestingService = fastapi.Depends(deps.get_testing_service),
):
    """Submit an answer for a problem (students only).

    Returns updated attempt statistics with the new score.
    """
    try:
        return await testing_service.submit_answer(answer_data, current_user.id)
    except service_exceptions.ServiceError as exc:
        if exc.code == "forbidden":
            raise http_errors.forbidden(exc.message, code=exc.code)
        if exc.code in ("homework_not_found", "problem_not_found"):
            raise http_errors.not_found(exc.message, code=exc.code)
        # problem_not_in_homework → 400
        raise http_errors.bad_request(exc.message, code=exc.code)


@router.post(
    "/homework/{homework_id}/submit",
    response_model=homework_schemas.StatisticsResponse,
)
async def submit_homework(
    homework_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_student),
    testing_service: testing_service_module.TestingService = fastapi.Depends(deps.get_testing_service),
):
    """Submit homework for final grading (students only)."""
    try:
        return await testing_service.submit_homework(homework_id, current_user.id)
    except service_exceptions.ServiceError as exc:
        if exc.code == "forbidden":
            raise http_errors.forbidden(exc.message, code=exc.code)
        # no_attempts → 404
        raise http_errors.not_found(exc.message, code=exc.code)


@router.get(
    "/homework/{homework_id}/status",
    response_model=homework_schemas.StatisticsResponse,
)
async def get_homework_status(
    homework_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_student),
    testing_service: testing_service_module.TestingService = fastapi.Depends(deps.get_testing_service),
):
    """Return current attempt statistics for a homework (students only)."""
    result = await testing_service.get_homework_status(homework_id, current_user.id)
    if result is None:
        raise http_errors.not_found("No attempts found for this homework")
    return result


@router.get("/dev-seed-info")
async def dev_seed_info(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> dict[str, tp.Any]:
    """Return seed credentials and IDs for frontend development (DEBUG only)."""
    if not core_config.settings.DEBUG:
        raise fastapi.HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Not found")

    user_repo = user_repository.UserRepository(db)
    teacher_repo = user_repository.TeacherRepository(db)
    classroom_repo = classroom_repository.ClassroomRepository(db)

    teacher_email = "teacher@wep.dev"
    teacher_user = await user_repo.get_by_email(teacher_email)
    if not teacher_user:
        return {
            "seeded": False,
            "hint": "Run `python -m app.scripts.seed_dev_data`.",
        }

    teacher_profile = await teacher_repo.get_by_user_id(teacher_user.id)
    classroom_items: list[dict[str, object]] = []
    if teacher_profile:
        classrooms = await classroom_repo.get_by_teacher(teacher_profile.id, skip=0, limit=100)
        for c in classrooms:
            classroom_items.append(
                {
                    "id": int(c.id),
                    "name": c.name,
                    "invite_code": c.invite_code,
                    "subject": c.subject,
                    "grade_level": c.grade_level,
                }
            )

    return {
        "seeded": True,
        "teacher": {"username_or_email": teacher_email, "password": "TeacherPass123!"},
        "students": {
            "password": "StudentPass123!",
            "emails": [f"student{i}@wep.dev" for i in range(1, 11)],
        },
        "classrooms": classroom_items,
        "ws": {"url_template": "ws://<host>/api/v1/classrooms/{classroom_id}/chat/ws?token=<jwt>"},
        "http": {"base_url": "http://<host>/api/v1"},
    }
