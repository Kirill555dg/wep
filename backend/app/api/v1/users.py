import fastapi
import sqlalchemy.ext.asyncio as sa_asyncio

from app.api import dependencies as deps
from app.api import http_errors
from app.db import session as db_session
from app.models import users as user_models
from app.repositories import user as user_repo
from app.schemas import users as user_schemas

router = fastapi.APIRouter()


@router.patch("/me", response_model=user_schemas.UserResponse)
async def update_me(
    data: user_schemas.UserUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> user_schemas.UserResponse:
    repo = user_repo.UserRepository(db)
    update_data = data.model_dump(exclude_none=True)
    if update_data:
        updated = await repo.update(current_user.id, update_data)
        if not updated:
            raise http_errors.not_found("User not found")
        return user_schemas.UserResponse.model_validate(updated)
    return user_schemas.UserResponse.model_validate(current_user)
