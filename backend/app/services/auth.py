"""
Authentication service.
"""

import uuid

import sqlalchemy.ext.asyncio as sa_asyncio

from app.core import security as core_security
from app.core import datetime_extensions as dte
from app.repositories import user as user_repository
from app.schemas import users as user_schemas
from app.services import exceptions as service_exceptions


class AuthService:
    """
    Service for authentication and user management.

    Failure semantics:
      - ``register_user`` raises :class:`ServiceError` with code
        ``"email_taken"`` when the email is already registered.
      - ``authenticate`` returns ``None`` for invalid credentials and raises
        :class:`ServiceError` with code ``"inactive_user"`` when the user is
        marked inactive.
      - ``get_*`` methods return ``None`` when the requested user is missing,
        so the calling route can decide whether ``404`` or another response
        is appropriate.
    """

    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.user_repo = user_repository.UserRepository(db)
        self.login_repo = user_repository.LoginDataRepository(db)
        self.teacher_repo = user_repository.TeacherRepository(db)
        self.student_repo = user_repository.StudentRepository(db)

    async def register_user(self, user_data: user_schemas.UserCreate) -> user_schemas.UserResponse:
        """Register a new user.

        Raises:
            ServiceError(code="email_taken"): If the email is already used.
        """
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
                "role": user_data.role.value,
            }
        )

        hashed_password = core_security.get_password_hash(user_data.password)
        await self.login_repo.create_for_user(user.id, hashed_password)

        # Create profile only for the active role. The other role can be
        # enabled later via `switch_role`.
        if user.role == user_schemas.UserRole.TEACHER.value:
            await self.teacher_repo.create({"user_id": user.id})
        else:
            await self.student_repo.create({"user_id": user.id})

        return user_schemas.UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            role=user_schemas.UserRole(user.role),
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
        """Authenticate user and return JWT token.

        Returns:
            ``TokenResponse`` on success, ``None`` for invalid credentials.

        Raises:
            ServiceError(code="inactive_user"): The user exists but is
                deactivated.
        """
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

        access_token = core_security.create_access_token(data={"sub": str(user.id), "role": user.role})

        return user_schemas.TokenResponse(
            access_token=access_token,
            user=user_schemas.UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                role=user_schemas.UserRole(user.role),
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
        )

    async def get_user_role(self, user_id: int) -> str | None:
        """Return active role for a user, or ``None`` if the user is missing."""
        user = await self.user_repo.get_by_id(user_id)
        return user.role if user else None

    async def get_roles(self, user_id: int) -> user_schemas.UserRolesResponse | None:
        """Return active and enabled roles, or ``None`` if user is missing."""
        user = await self.user_repo.get_with_profile(user_id)
        if not user:
            return None

        enabled: list[user_schemas.UserRole] = []
        if user.student is not None:
            enabled.append(user_schemas.UserRole.STUDENT)
        if user.teacher is not None:
            enabled.append(user_schemas.UserRole.TEACHER)

        return user_schemas.UserRolesResponse(
            active_role=user_schemas.UserRole(user.role),
            enabled_roles=enabled,
        )

    async def switch_role(
        self,
        user_id: int,
        role: user_schemas.UserRole,
    ) -> user_schemas.UserRolesResponse | None:
        """Switch the active role.

        Returns:
            Updated roles, or ``None`` if user is missing.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None

        # Ensure target role profile exists.
        if role == user_schemas.UserRole.TEACHER:
            if not await self.teacher_repo.get_by_user_id(user_id):
                await self.teacher_repo.create({"user_id": user_id})
        else:
            if not await self.student_repo.get_by_user_id(user_id):
                await self.student_repo.create({"user_id": user_id})

        await self.user_repo.update(user_id, {"role": role.value})
        return await self.get_roles(user_id)

    async def get_current_user(self, user_id: int) -> user_schemas.UserResponse | None:
        """Return the current authenticated user or ``None`` if missing."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        return user_schemas.UserResponse.model_validate(user)
