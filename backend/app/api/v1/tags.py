import fastapi
import starlette.status as http_status
import sqlalchemy.ext.asyncio as sa_asyncio

from app.api import dependencies as deps
from app.db import session as db_session
from app.models import users as user_models
from app.repositories import test_constructor as tc_repos
from app.schemas import test_constructor as tc_schemas

router = fastapi.APIRouter()


def _get_tag_repo(db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db)) -> tc_repos.TagRepository:
    return tc_repos.TagRepository(db)


@router.get("/", response_model=list[tc_schemas.TagResponse])
async def list_tags(
    repo: tc_repos.TagRepository = fastapi.Depends(_get_tag_repo),
) -> list[tc_schemas.TagResponse]:
    tags = await repo.get_all()
    return [tc_schemas.TagResponse.model_validate(t) for t in tags]


@router.post("/", response_model=tc_schemas.TagResponse, status_code=http_status.HTTP_201_CREATED)
async def create_tag(
    data: tc_schemas.TagCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    repo: tc_repos.TagRepository = fastapi.Depends(_get_tag_repo),
) -> tc_schemas.TagResponse:
    tag = await repo.get_or_create(data.name)
    return tc_schemas.TagResponse.model_validate(tag)
