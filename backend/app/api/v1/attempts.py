import datetime as dt

import fastapi
import starlette.status as http_status
import sqlalchemy.ext.asyncio as sa_asyncio

from app.api import dependencies as deps
from app.api import http_errors
from app.db import session as db_session
from app.models import users as user_models
from app.schemas import attempts as attempt_schemas
from app.schemas.pagination import Page
from app.schemas import test_constructor as tc_schemas
from app.services import attempt_service as attempt_svc
from app.services import exceptions as svc_exc

router = fastapi.APIRouter()


def _get_attempt_service(db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db)) -> attempt_svc.AttemptService:
    return attempt_svc.AttemptService(db)


@router.post("/", response_model=tc_schemas.AttemptResponse, status_code=http_status.HTTP_201_CREATED)
async def start_attempt(
    data: tc_schemas.AttemptStartRequest,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: attempt_svc.AttemptService = fastapi.Depends(_get_attempt_service),
) -> tc_schemas.AttemptResponse:
    try:
        return await svc.start_attempt(data.test_id, current_user.id)
    except svc_exc.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "attempt_already_active":
            raise http_errors.bad_request(exc.message, code=exc.code)
        raise


@router.get("/", response_model=Page[attempt_schemas.AttemptSummary])
async def list_my_attempts(
    skip: int = fastapi.Query(0, ge=0),
    limit: int = fastapi.Query(20, ge=1, le=100),
    status: str | None = fastapi.Query(None),
    test_id: int | None = fastapi.Query(None),
    date_from: dt.datetime | None = fastapi.Query(None),
    date_to: dt.datetime | None = fastapi.Query(None),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: attempt_svc.AttemptService = fastapi.Depends(_get_attempt_service),
) -> Page[attempt_schemas.AttemptSummary]:
    rows, total = await svc.attempt_repo.list_by_user(
        current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        test_id=test_id,
        date_from=date_from,
        date_to=date_to,
    )
    items = []
    for row in rows:
        minutes = None
        if row.finished_at and row.started_at:
            minutes = int((row.finished_at - row.started_at).total_seconds() // 60)
        items.append(attempt_schemas.AttemptSummary(
            id=row.id,
            test_id=row.test_id,
            test_title=row.test.title if row.test else "",
            status=row.status,
            score=row.score,
            max_score=row.max_score,
            started_at=row.started_at,
            finished_at=row.finished_at,
            time_spent_minutes=minutes,
        ))
    return Page(items=items, total=total, skip=skip, limit=limit)


@router.get("/active", response_model=attempt_schemas.ActiveAttemptResponse)
async def get_active_attempt(
    test_id: int = fastapi.Query(...),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: attempt_svc.AttemptService = fastapi.Depends(_get_attempt_service),
) -> attempt_schemas.ActiveAttemptResponse:
    total = await svc.attempt_repo.count_by_user(current_user.id, test_id=test_id)
    active = await svc.attempt_repo.get_active_for_user_test(current_user.id, test_id)
    return attempt_schemas.ActiveAttemptResponse(
        has_active=active is not None,
        attempt_id=active.id if active else None,
        status=active.status if active else None,
        attempts_used=total,
    )


@router.get("/{attempt_id}", response_model=tc_schemas.AttemptResponse)
async def get_attempt(
    attempt_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: attempt_svc.AttemptService = fastapi.Depends(_get_attempt_service),
) -> tc_schemas.AttemptResponse:
    attempt = await svc.attempt_repo.get_by_id(attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise http_errors.not_found("Attempt not found")
    return tc_schemas.AttemptResponse.model_validate(attempt)


@router.post("/{attempt_id}/answers", response_model=tc_schemas.AnswerResponse)
async def submit_answer(
    attempt_id: int,
    data: tc_schemas.AnswerSubmitRequest,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: attempt_svc.AttemptService = fastapi.Depends(_get_attempt_service),
) -> tc_schemas.AnswerResponse:
    try:
        return await svc.submit_answer(attempt_id, current_user.id, data)
    except svc_exc.ServiceError as exc:
        if exc.code == "attempt_not_found":
            raise http_errors.not_found("Attempt not found")
        if exc.code == "attempt_finished":
            raise http_errors.bad_request(exc.message, code=exc.code)
        if exc.code == "question_not_found":
            raise http_errors.not_found("Question not found in test")
        raise


@router.post("/{attempt_id}/bulk-answers", response_model=attempt_schemas.BulkAnswersResponse)
async def submit_bulk_answers(
    attempt_id: int,
    data: attempt_schemas.BulkAnswersRequest,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: attempt_svc.AttemptService = fastapi.Depends(_get_attempt_service),
) -> attempt_schemas.BulkAnswersResponse:
    attempt = await svc.attempt_repo.get_by_id(attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise http_errors.not_found("Attempt not found")

    questions = await svc.question_repo.get_by_test(attempt.test_id)
    valid_question_ids = {q.id for q in questions}
    saved = 0
    errors: list[str] = []
    for ans in data.answers:
        if ans.question_id not in valid_question_ids:
            errors.append(f"Question {ans.question_id} does not belong to this test")
            continue
        await svc.answer_repo.upsert(attempt_id, ans.question_id, {
            "selected_option_ids": ans.selected_option_ids,
            "text_answer": ans.text_answer,
        })
        saved += 1

    return attempt_schemas.BulkAnswersResponse(saved=saved, errors=errors or None)


@router.post("/{attempt_id}/finish", response_model=tc_schemas.AttemptResultResponse)
async def finish_attempt(
    attempt_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: attempt_svc.AttemptService = fastapi.Depends(_get_attempt_service),
) -> tc_schemas.AttemptResultResponse:
    try:
        return await svc.finish_attempt(attempt_id, current_user.id)
    except svc_exc.ServiceError as exc:
        if exc.code == "attempt_not_found":
            raise http_errors.not_found("Attempt not found")
        raise


@router.get("/{attempt_id}/result", response_model=tc_schemas.AttemptResultResponse)
async def get_result(
    attempt_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: attempt_svc.AttemptService = fastapi.Depends(_get_attempt_service),
) -> tc_schemas.AttemptResultResponse:
    try:
        return await svc.get_result(attempt_id, current_user.id)
    except svc_exc.ServiceError as exc:
        if exc.code == "attempt_not_found":
            raise http_errors.not_found("Attempt not found")
        raise
