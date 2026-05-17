"""
Stats API: author statistics.
"""

import fastapi
from sqlalchemy.ext import asyncio as sa_asyncio

from app.api import dependencies as deps
from app.api import http_errors
from app.db import session as db_session
from app.models import users as user_models
from app.schemas.test_constructor import AuthorStatsResponse, TestStatsResponse
from app.services import exceptions as service_exceptions
from app.services.catalog_service import AuthorStatsService

router = fastapi.APIRouter()


def _get_stats_service(db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db)) -> AuthorStatsService:
    return AuthorStatsService(db)


@router.get("/me", response_model=AuthorStatsResponse)
async def get_author_stats(
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: AuthorStatsService = fastapi.Depends(_get_stats_service),
) -> AuthorStatsResponse:
    return await svc.get_author_stats(current_user.id)


@router.get("/tests/{test_id}", response_model=TestStatsResponse)
async def get_test_stats(
    test_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: AuthorStatsService = fastapi.Depends(_get_stats_service),
) -> TestStatsResponse:
    try:
        return await svc.get_test_stats(test_id, current_user.id)
    except service_exceptions.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise
