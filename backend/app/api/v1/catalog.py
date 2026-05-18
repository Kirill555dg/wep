import fastapi
import sqlalchemy.ext.asyncio as sa_asyncio

from app.api import http_errors
from app.api.v1 import tests as tests_router
from app.db import session as db_session
from app.schemas import test_constructor as tc_schemas
from app.services import catalog_service as catalog_svc
from app.services import exceptions as svc_exc

router = fastapi.APIRouter()


def _get_catalog_service(db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db)) -> catalog_svc.CatalogService:
    return catalog_svc.CatalogService(db)


@router.get("/", response_model=list[tc_schemas.TestResponse])
async def search_catalog(
    q: str | None = None,
    tags: list[str] = fastapi.Query(default_factory=list),
    author_id: int | None = None,
    skip: int = 0,
    limit: int = 20,
    svc: catalog_svc.CatalogService = fastapi.Depends(_get_catalog_service),
) -> list[tc_schemas.TestResponse]:
    params = tc_schemas.CatalogSearchParams(q=q, tags=tags, author_id=author_id, skip=skip, limit=limit)
    results, _ = await svc.search_public_tests(params)
    return [tests_router._map_test_response(t) for t in results]


@router.get("/{test_id}", response_model=tc_schemas.TestDetailResponse)
async def get_public_test(
    test_id: int,
    svc: catalog_svc.CatalogService = fastapi.Depends(_get_catalog_service),
) -> tc_schemas.TestDetailResponse:
    try:
        test = await svc.get_public_test_detail(test_id)
    except svc_exc.ServiceError as exc:
        if exc.code == "test_not_found":
            raise http_errors.not_found("Test not found")
        raise
    return tests_router._map_detail(test)
