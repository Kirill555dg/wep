"""
Tests API: CRUD for tests and questions.
"""

import fastapi
from fastapi import status as http_status
from sqlalchemy.ext import asyncio as sa_asyncio

from app.api import dependencies as deps
from app.api import http_errors
from app.db import session as db_session
from app.models import users as user_models
from app.schemas.test_constructor import (
    QuestionAuthorResponse,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
    TestAuthorDetailResponse,
    TestCreate,
    TestDetailResponse,
    TestResponse,
    TestUpdate,
)
from app.services import exceptions as service_exceptions
from app.services.test_service import TestService

router = fastapi.APIRouter()


def _get_test_service(db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db)) -> TestService:
    return TestService(db)


@router.post("/", response_model=TestResponse, status_code=http_status.HTTP_201_CREATED)
async def create_test(
    data: TestCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: TestService = fastapi.Depends(_get_test_service),
) -> TestResponse:
    test = await svc.create_test(author_id=current_user.id, data=data)
    return _map_test_response(test)


@router.get("/", response_model=list[TestResponse])
async def list_my_tests(
    skip: int = 0,
    limit: int = 20,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: TestService = fastapi.Depends(_get_test_service),
) -> list[TestResponse]:
    tests, _ = await svc.list_author_tests(current_user.id, skip, limit)
    return [_map_test_response(t) for t in tests]


@router.get("/{test_id}", response_model=TestAuthorDetailResponse | TestDetailResponse)
async def get_test(
    test_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: TestService = fastapi.Depends(_get_test_service),
) -> TestAuthorDetailResponse | TestDetailResponse:
    try:
        test = await svc.get_test(test_id, current_user.id)
    except service_exceptions.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "test_access_denied":
            raise http_errors.forbidden("Access denied")
        raise
    if test.author_id == current_user.id:
        return _map_author_detail(test)
    return _map_detail(test)


@router.patch("/{test_id}", response_model=TestResponse)
async def update_test(
    test_id: int,
    data: TestUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: TestService = fastapi.Depends(_get_test_service),
) -> TestResponse:
    try:
        test = await svc.update_test(test_id, current_user.id, data)
    except service_exceptions.ServiceError as exc:
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
    svc: TestService = fastapi.Depends(_get_test_service),
) -> None:
    try:
        await svc.delete_test(test_id, current_user.id)
    except service_exceptions.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise


@router.post("/{test_id}/questions", response_model=QuestionAuthorResponse, status_code=http_status.HTTP_201_CREATED)
async def add_question(
    test_id: int,
    data: QuestionCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: TestService = fastapi.Depends(_get_test_service),
) -> QuestionAuthorResponse:
    try:
        q = await svc.add_question(test_id, current_user.id, data)
    except service_exceptions.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise
    return QuestionAuthorResponse.model_validate(q)


@router.patch("/{test_id}/questions/{question_id}", response_model=QuestionAuthorResponse)
async def update_question(
    test_id: int,
    question_id: int,
    data: QuestionUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: TestService = fastapi.Depends(_get_test_service),
) -> QuestionAuthorResponse:
    try:
        q = await svc.update_question(question_id, current_user.id, data)
    except service_exceptions.ServiceError as exc:
        if exc.code in ("question_not_found", "test_not_found"):
            raise http_errors.not_found("Question not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise
    return QuestionAuthorResponse.model_validate(q)


@router.delete("/{test_id}/questions/{question_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_question(
    test_id: int,
    question_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: TestService = fastapi.Depends(_get_test_service),
) -> None:
    try:
        await svc.delete_question(question_id, current_user.id)
    except service_exceptions.ServiceError as exc:
        if exc.code in ("question_not_found", "test_not_found"):
            raise http_errors.not_found("Question not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise


# --- mapping helpers ---

def _map_test_response(test) -> TestResponse:
    from app.schemas.test_constructor import TagResponse
    tags = [TagResponse.model_validate(tt.tag) for tt in (test.test_tags or [])]
    questions_count = len(test.questions) if test.questions else 0
    return TestResponse(
        id=test.id,
        author_id=test.author_id,
        title=test.title,
        description=test.description,
        is_public=test.is_public,
        time_limit_minutes=test.time_limit_minutes,
        questions_count=questions_count,
        tags=tags,
        created_at=test.created_at,
        updated_at=test.updated_at,
    )


def _map_detail(test) -> TestDetailResponse:
    from app.schemas.test_constructor import OptionResponse, QuestionResponse, TagResponse
    tags = [TagResponse.model_validate(tt.tag) for tt in (test.test_tags or [])]
    questions = [
        QuestionResponse(
            id=q.id,
            question_type=q.question_type,
            text=q.text,
            order_number=q.order_number,
            points=q.points,
            image_url=q.image_url,
            options=[OptionResponse.model_validate(o) for o in q.options],
        )
        for q in (test.questions or [])
    ]
    return TestDetailResponse(
        id=test.id,
        author_id=test.author_id,
        title=test.title,
        description=test.description,
        is_public=test.is_public,
        time_limit_minutes=test.time_limit_minutes,
        questions_count=len(questions),
        tags=tags,
        created_at=test.created_at,
        updated_at=test.updated_at,
        questions=questions,
    )


def _map_author_detail(test) -> TestAuthorDetailResponse:
    from app.schemas.test_constructor import OptionAuthorResponse, QuestionAuthorResponse, TagResponse
    tags = [TagResponse.model_validate(tt.tag) for tt in (test.test_tags or [])]
    questions = [
        QuestionAuthorResponse(
            id=q.id,
            question_type=q.question_type,
            text=q.text,
            order_number=q.order_number,
            points=q.points,
            explanation=q.explanation,
            image_url=q.image_url,
            options=[OptionAuthorResponse.model_validate(o) for o in q.options],
        )
        for q in (test.questions or [])
    ]
    return TestAuthorDetailResponse(
        id=test.id,
        author_id=test.author_id,
        title=test.title,
        description=test.description,
        is_public=test.is_public,
        time_limit_minutes=test.time_limit_minutes,
        questions_count=len(questions),
        tags=tags,
        created_at=test.created_at,
        updated_at=test.updated_at,
        questions=questions,
    )
