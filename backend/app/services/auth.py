import uuid

import sqlalchemy.ext.asyncio as sa_asyncio

from app.core import security as core_security
from app.core import datetime_extensions as dte
from app.repositories import user as user_repository
from app.schemas import users as user_schemas
from app.services import exceptions as service_exceptions


class AuthService:
    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.user_repo = user_repository.UserRepository(db)
        self.login_repo = user_repository.LoginDataRepository(db)

    async def register_user(self, user_data: user_schemas.UserCreate) -> user_schemas.UserResponse:
        existing_email = await self.user_repo.get_by_email(user_data.email)
        if existing_email:
            raise service_exceptions.ServiceError("Email already registered", code="email_taken")

        if user_data.username:
            if await self.user_repo.get_by_username(user_data.username):
                raise service_exceptions.ServiceError("Username already taken", code="username_taken")
            generated_username = user_data.username
        else:
            base = user_data.email.split("@")[0]
            generated_username = f"{base}_{uuid.uuid4().hex[:8]}"

        user = await self.user_repo.create(
            {
                "username": generated_username,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "middle_name": user_data.middle_name,
                "full_name": user_data.full_name
                or " ".join(
                    part for part in [user_data.first_name, user_data.middle_name, user_data.last_name] if part
                ),
                "avatar_url": user_data.avatar_url,
                "is_active": True,
            }
        )

        hashed_password = core_security.get_password_hash(user_data.password)
        await self.login_repo.create_for_user(user.id, hashed_password)

        return user_schemas.UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def authenticate(
        self,
        login_data: user_schemas.LoginRequest,
    ) -> user_schemas.TokenResponse | None:
        user = await self.user_repo.get_by_username_or_email(login_data.username_or_email)
        if not user:
            return None

        if not user.is_active:
            raise service_exceptions.ServiceError(
                "User account is inactive",
                code="inactive_user",
            )

        login_info = await self.login_repo.get_by_user_id(user.id)
        if not login_info:
            return None

        if not core_security.verify_password(login_data.password, login_info.hashed_password):
            return None

        await self.login_repo.update(login_info.id, {"last_login": dte.utc_now()})

        access_token = core_security.create_access_token(data={"sub": str(user.id)})

        return user_schemas.TokenResponse(
            access_token=access_token,
            user=user_schemas.UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
        )

    async def get_current_user(self, user_id: int) -> user_schemas.UserResponse | None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        return user_schemas.UserResponse.model_validate(user)
