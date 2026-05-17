import fastapi
import sqlalchemy.ext.asyncio as sa_asyncio
import starlette.status as http_status

from app.api import dependencies as deps
from app.api import http_errors
from app.db import session as db_session
from app.models import users as user_models
from app.schemas import test_constructor as tc_schemas
from app.services import exceptions as svc_exc
from app.services import test_service as test_svc

router = fastapi.APIRouter()


def _get_test_service(db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db)) -> test_svc.TestService:
    return test_svc.TestService(db)


@router.post("/", response_model=tc_schemas.TestResponse, status_code=http_status.HTTP_201_CREATED)
async def create_test(
    data: tc_schemas.TestCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: test_svc.TestService = fastapi.Depends(_get_test_service),
) -> tc_schemas.TestResponse:
    test = await svc.create_test(author_id=current_user.id, data=data)
    return _map_test_response(test)


@router.get("/", response_model=list[tc_schemas.TestResponse])
async def list_my_tests(
    skip: int = 0,
    limit: int = 20,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: test_svc.TestService = fastapi.Depends(_get_test_service),
) -> list[tc_schemas.TestResponse]:
    tests, _ = await svc.list_author_tests(current_user.id, skip, limit)
    return [_map_test_response(t) for t in tests]


@router.get("/{test_id}", response_model=tc_schemas.TestAuthorDetailResponse | tc_schemas.TestDetailResponse)
async def get_test(
    test_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: test_svc.TestService = fastapi.Depends(_get_test_service),
) -> tc_schemas.TestAuthorDetailResponse | tc_schemas.TestDetailResponse:
    try:
        test = await svc.get_test(test_id, current_user.id)
    except svc_exc.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "test_access_denied":
            raise http_errors.forbidden("Access denied")
        raise
    if test.author_id == current_user.id:
        return _map_author_detail(test)
    return _map_detail(test)


@router.patch("/{test_id}", response_model=tc_schemas.TestResponse)
async def update_test(
    test_id: int,
    data: tc_schemas.TestUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: test_svc.TestService = fastapi.Depends(_get_test_service),
) -> tc_schemas.TestResponse:
    try:
        test = await svc.update_test(test_id, current_user.id, data)
    except svc_exc.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise
    return _map_test_response(test)


@router.delete("/{test_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_test(
    test_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: test_svc.TestService = fastapi.Depends(_get_test_service),
) -> None:
    try:
        await svc.delete_test(test_id, current_user.id)
    except svc_exc.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise


@router.post("/{test_id}/questions", response_model=tc_schemas.QuestionAuthorResponse, status_code=http_status.HTTP_201_CREATED)
async def add_question(
    test_id: int,
    data: tc_schemas.QuestionCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: test_svc.TestService = fastapi.Depends(_get_test_service),
) -> tc_schemas.QuestionAuthorResponse:
    try:
        q = await svc.add_question(test_id, current_user.id, data)
    except svc_exc.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise
    return tc_schemas.QuestionAuthorResponse.model_validate(q)


@router.patch("/{test_id}/questions/{question_id}", response_model=tc_schemas.QuestionAuthorResponse)
async def update_question(
    test_id: int,
    question_id: int,
    data: tc_schemas.QuestionUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: test_svc.TestService = fastapi.Depends(_get_test_service),
) -> tc_schemas.QuestionAuthorResponse:
    try:
        q = await svc.update_question(question_id, current_user.id, data)
    except svc_exc.ServiceError as exc:
        if exc.code in ("question_not_found", "test_not_found"):
            raise http_errors.not_found("Question not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise
    return tc_schemas.QuestionAuthorResponse.model_validate(q)


@router.delete("/{test_id}/questions/{question_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_question(
    test_id: int,
    question_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: test_svc.TestService = fastapi.Depends(_get_test_service),
) -> None:
    try:
        await svc.delete_question(question_id, current_user.id)
    except svc_exc.ServiceError as exc:
        if exc.code in ("question_not_found", "test_not_found"):
            raise http_errors.not_found("Question not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise


def _map_test_response(test: object) -> tc_schemas.TestResponse:
    tags = [tc_schemas.TagResponse.model_validate(tt.tag) for tt in (test.test_tags or [])]  # type: ignore[attr-defined]
    questions_count = len(test.questions) if test.questions else 0  # type: ignore[attr-defined]
    return tc_schemas.TestResponse(
        id=test.id,  # type: ignore[attr-defined]
        author_id=test.author_id,  # type: ignore[attr-defined]
        title=test.title,  # type: ignore[attr-defined]
        description=test.description,  # type: ignore[attr-defined]
        is_public=test.is_public,  # type: ignore[attr-defined]
        time_limit_minutes=test.time_limit_minutes,  # type: ignore[attr-defined]
        questions_count=questions_count,
        tags=tags,
        created_at=test.created_at,  # type: ignore[attr-defined]
        updated_at=test.updated_at,  # type: ignore[attr-defined]
    )


def _map_detail(test: object) -> tc_schemas.TestDetailResponse:
    tags = [tc_schemas.TagResponse.model_validate(tt.tag) for tt in (test.test_tags or [])]  # type: ignore[attr-defined]
    questions = [
        tc_schemas.QuestionResponse(
            id=q.id,
            question_type=q.question_type,
            text=q.text,
            order_number=q.order_number,
            points=q.points,
            image_url=q.image_url,
            options=[tc_schemas.OptionResponse.model_validate(o) for o in q.options],
        )
        for q in (test.questions or [])  # type: ignore[attr-defined]
    ]
    return tc_schemas.TestDetailResponse(
        id=test.id,  # type: ignore[attr-defined]
        author_id=test.author_id,  # type: ignore[attr-defined]
        title=test.title,  # type: ignore[attr-defined]
        description=test.description,  # type: ignore[attr-defined]
        is_public=test.is_public,  # type: ignore[attr-defined]
        time_limit_minutes=test.time_limit_minutes,  # type: ignore[attr-defined]
        questions_count=len(questions),
        tags=tags,
        created_at=test.created_at,  # type: ignore[attr-defined]
        updated_at=test.updated_at,  # type: ignore[attr-defined]
        questions=questions,
    )


def _map_author_detail(test: object) -> tc_schemas.TestAuthorDetailResponse:
    tags = [tc_schemas.TagResponse.model_validate(tt.tag) for tt in (test.test_tags or [])]  # type: ignore[attr-defined]
    questions = [
        tc_schemas.QuestionAuthorResponse(
            id=q.id,
            question_type=q.question_type,
            text=q.text,
            order_number=q.order_number,
            points=q.points,
            explanation=q.explanation,
            correct_answer=q.correct_answer,
            image_url=q.image_url,
            options=[tc_schemas.OptionAuthorResponse.model_validate(o) for o in q.options],
        )
        for q in (test.questions or [])  # type: ignore[attr-defined]
    ]
    return tc_schemas.TestAuthorDetailResponse(
        id=test.id,  # type: ignore[attr-defined]
        author_id=test.author_id,  # type: ignore[attr-defined]
        title=test.title,  # type: ignore[attr-defined]
        description=test.description,  # type: ignore[attr-defined]
        is_public=test.is_public,  # type: ignore[attr-defined]
        time_limit_minutes=test.time_limit_minutes,  # type: ignore[attr-defined]
        questions_count=len(questions),
        tags=tags,
        created_at=test.created_at,  # type: ignore[attr-defined]
        updated_at=test.updated_at,  # type: ignore[attr-defined]
        questions=questions,
    )
