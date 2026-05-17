"""
Tags API.
"""

import fastapi
from fastapi import status as http_status
from sqlalchemy.ext import asyncio as sa_asyncio

from app.api import dependencies as deps
from app.db import session as db_session
from app.models import users as user_models
from app.schemas.test_constructor import TagCreate, TagResponse
from app.repositories.test_constructor import TagRepository

router = fastapi.APIRouter()


def _get_tag_repo(db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db)) -> TagRepository:
    return TagRepository(db)


@router.get("/", response_model=list[TagResponse])
async def list_tags(
    repo: TagRepository = fastapi.Depends(_get_tag_repo),
) -> list[TagResponse]:
    tags = await repo.get_all()
    return [TagResponse.model_validate(t) for t in tags]


@router.post("/", response_model=TagResponse, status_code=http_status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    repo: TagRepository = fastapi.Depends(_get_tag_repo),
) -> TagResponse:
    tag = await repo.get_or_create(data.name)
    return TagResponse.model_validate(tag)
