"""
Catalog API: public test search.
"""

import fastapi
from sqlalchemy.ext import asyncio as sa_asyncio

from app.api import http_errors
from app.db import session as db_session
from app.schemas.test_constructor import CatalogSearchParams, TestDetailResponse, TestResponse
from app.services import exceptions as service_exceptions
from app.services.catalog_service import CatalogService

router = fastapi.APIRouter()


def _get_catalog_service(db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db)) -> CatalogService:
    return CatalogService(db)


@router.get("/", response_model=list[TestResponse])
async def search_catalog(
    q: str | None = None,
    tags: list[str] = fastapi.Query(default_factory=list),
    skip: int = 0,
    limit: int = 20,
    svc: CatalogService = fastapi.Depends(_get_catalog_service),
) -> list[TestResponse]:
    from app.api.v1.tests import _map_test_response
    params = CatalogSearchParams(q=q, tags=tags, skip=skip, limit=limit)
    tests, _ = await svc.search_public_tests(params)
    return [_map_test_response(t) for t in tests]


@router.get("/{test_id}", response_model=TestDetailResponse)
async def get_public_test(
    test_id: int,
    svc: CatalogService = fastapi.Depends(_get_catalog_service),
) -> TestDetailResponse:
    from app.api.v1.tests import _map_detail
    try:
        test = await svc.get_public_test_detail(test_id)
    except service_exceptions.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        raise
    return _map_detail(test)
