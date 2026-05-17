"""
Attempts API: start, submit answers, finish, get result.
"""

import fastapi
from fastapi import status as http_status
from sqlalchemy.ext import asyncio as sa_asyncio

from app.api import dependencies as deps
from app.api import http_errors
from app.db import session as db_session
from app.models import users as user_models
from app.schemas.test_constructor import (
    AnswerResponse,
    AnswerSubmitRequest,
    AttemptResponse,
    AttemptResultResponse,
    AttemptStartRequest,
)
from app.services import exceptions as service_exceptions
from app.services.attempt_service import AttemptService

router = fastapi.APIRouter()


def _get_attempt_service(db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db)) -> AttemptService:
    return AttemptService(db)


@router.post("/", response_model=AttemptResponse, status_code=http_status.HTTP_201_CREATED)
async def start_attempt(
    data: AttemptStartRequest,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: AttemptService = fastapi.Depends(_get_attempt_service),
) -> AttemptResponse:
    try:
        return await svc.start_attempt(data.test_id, current_user.id)
    except service_exceptions.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "attempt_already_active":
            raise http_errors.bad_request(exc.message, code=exc.code)
        raise


@router.get("/{attempt_id}", response_model=AttemptResponse)
async def get_attempt(
    attempt_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: AttemptService = fastapi.Depends(_get_attempt_service),
) -> AttemptResponse:
    from app.repositories.test_constructor import AttemptRepository
    from app.db import session as db_session_module
    repo = svc.attempt_repo
    attempt = await repo.get_by_id(attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise http_errors.not_found("Attempt not found")
    return AttemptResponse.model_validate(attempt)


@router.post("/{attempt_id}/answers", response_model=AnswerResponse)
async def submit_answer(
    attempt_id: int,
    data: AnswerSubmitRequest,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: AttemptService = fastapi.Depends(_get_attempt_service),
) -> AnswerResponse:
    try:
        return await svc.submit_answer(attempt_id, current_user.id, data)  # type: ignore[return-value]
    except service_exceptions.ServiceError as exc:
        if exc.code == "attempt_not_found":
            raise http_errors.not_found("Attempt not found")
        if exc.code == "attempt_finished":
            raise http_errors.bad_request(exc.message, code=exc.code)
        if exc.code == "question_not_found":
            raise http_errors.not_found("Question not found in test")
        raise


@router.post("/{attempt_id}/finish", response_model=AttemptResultResponse)
async def finish_attempt(
    attempt_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: AttemptService = fastapi.Depends(_get_attempt_service),
) -> AttemptResultResponse:
    try:
        return await svc.finish_attempt(attempt_id, current_user.id)
    except service_exceptions.ServiceError as exc:
        if exc.code == "attempt_not_found":
            raise http_errors.not_found("Attempt not found")
        raise


@router.get("/{attempt_id}/result", response_model=AttemptResultResponse)
async def get_result(
    attempt_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: AttemptService = fastapi.Depends(_get_attempt_service),
) -> AttemptResultResponse:
    try:
        return await svc.get_result(attempt_id, current_user.id)
    except service_exceptions.ServiceError as exc:
        if exc.code == "attempt_not_found":
            raise http_errors.not_found("Attempt not found")
        raise
