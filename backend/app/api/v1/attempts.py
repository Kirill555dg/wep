import fastapi
import starlette.status as http_status
import sqlalchemy.ext.asyncio as sa_asyncio

from app.api import dependencies as deps
from app.api import http_errors
from app.db import session as db_session
from app.models import users as user_models
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
