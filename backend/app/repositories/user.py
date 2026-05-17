import typing as tp

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio
import sqlalchemy.orm as sqla_orm

from app.models import users as user_models
from app.repositories import base as base_repo


class UserRepository(base_repo.BaseRepository[user_models.User]):
    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(user_models.User, db)

    async def get_by_username(self, username: str) -> user_models.User | None:
        stmt = sa.select(user_models.User).where(user_models.User.username == username)
        return tp.cast(user_models.User | None, await self._scalar_one_or_none(stmt))

    async def get_by_email(self, email: str) -> user_models.User | None:
        stmt = sa.select(user_models.User).where(user_models.User.email == email)
        return tp.cast(user_models.User | None, await self._scalar_one_or_none(stmt))

    async def get_by_username_or_email(self, username_or_email: str) -> user_models.User | None:
        stmt = sa.select(user_models.User).where(
            sa.or_(user_models.User.username == username_or_email, user_models.User.email == username_or_email)
        )
        return tp.cast(user_models.User | None, await self._scalar_one_or_none(stmt))

    async def get_with_login_data(self, user_id: int) -> user_models.User | None:
        stmt = (
            sa.select(user_models.User)
            .options(sqla_orm.joinedload(user_models.User.login_data))
            .where(user_models.User.id == user_id)
        )
        return tp.cast(user_models.User | None, await self._scalar_one_or_none(stmt))

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> list[user_models.User]:
        stmt = sa.select(user_models.User).where(user_models.User.is_active).offset(skip).limit(limit)
        return tp.cast(list[user_models.User], await self._scalars_all(stmt))


class LoginDataRepository(base_repo.BaseRepository[user_models.LoginData]):
    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(user_models.LoginData, db)

    async def get_by_user_id(self, user_id: int) -> user_models.LoginData | None:
        stmt = sa.select(user_models.LoginData).where(user_models.LoginData.user_id == user_id)
        return tp.cast(user_models.LoginData | None, await self._scalar_one_or_none(stmt))

    async def create_for_user(self, user_id: int, hashed_password: str) -> user_models.LoginData:
        return await self.create({"user_id": user_id, "hashed_password": hashed_password})

    async def update_password(self, user_id: int, hashed_password: str) -> user_models.LoginData | None:
        login_data = await self.get_by_user_id(user_id)
        if not login_data:
            return None
        return await self.update(login_data.id, {"hashed_password": hashed_password})
