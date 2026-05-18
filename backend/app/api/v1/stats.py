import calendar
import datetime as dt

import fastapi
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio

from app.api import dependencies as deps
from app.api import http_errors
from app.db import session as db_session
from app.models import test_constructor as tc_models
from app.models import users as user_models
from app.schemas import stats as stats_schemas
from app.schemas import test_constructor as tc_schemas
from app.services import catalog_service as catalog_svc
from app.services import exceptions as svc_exc

router = fastapi.APIRouter()


def _get_stats_service(db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db)) -> catalog_svc.AuthorStatsService:
    return catalog_svc.AuthorStatsService(db)


@router.get("/me", response_model=tc_schemas.AuthorStatsResponse)
async def get_author_stats(
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: catalog_svc.AuthorStatsService = fastapi.Depends(_get_stats_service),
) -> tc_schemas.AuthorStatsResponse:
    return await svc.get_author_stats(current_user.id)


@router.get("/tests/{test_id}", response_model=tc_schemas.TestStatsResponse)
async def get_test_stats(
    test_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    svc: catalog_svc.AuthorStatsService = fastapi.Depends(_get_stats_service),
) -> tc_schemas.TestStatsResponse:
    try:
        return await svc.get_test_stats(test_id, current_user.id)
    except svc_exc.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        if exc.code == "not_author":
            raise http_errors.forbidden("Not the author")
        raise


@router.get("/calendar", response_model=stats_schemas.CalendarResponse)
async def get_calendar(
    year: int = fastapi.Query(default_factory=lambda: dt.datetime.now().year),
    month: int = fastapi.Query(default_factory=lambda: dt.datetime.now().month),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> stats_schemas.CalendarResponse:
    start_date = dt.datetime(year, month, 1, tzinfo=dt.timezone.utc)
    if month == 12:
        end_date = dt.datetime(year + 1, 1, 1, tzinfo=dt.timezone.utc)
    else:
        end_date = dt.datetime(year, month + 1, 1, tzinfo=dt.timezone.utc)

    stmt = (
        sa.select(
            sa.func.date_trunc("day", tc_models.Attempt.started_at).label("day"),
            sa.func.count(tc_models.Attempt.id).label("count"),
        )
        .where(
            tc_models.Attempt.user_id == current_user.id,
            tc_models.Attempt.status == "completed",
            tc_models.Attempt.started_at >= start_date,
            tc_models.Attempt.started_at < end_date,
        )
        .group_by(sa.func.date_trunc("day", tc_models.Attempt.started_at))
    )

    result = await db.execute(stmt)
    rows = result.all()

    days_in_month = calendar.monthrange(year, month)[1]
    days = {}
    for d in range(1, days_in_month + 1):
        date_str = f"{year}-{month:02d}-{d:02d}"
        days[date_str] = 0

    for row in rows:
        date_str = row.day.strftime("%Y-%m-%d")
        days[date_str] = row.count

    return stats_schemas.CalendarResponse(year=year, month=month, days=days)
