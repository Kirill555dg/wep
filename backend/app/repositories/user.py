"""
User repository
"""

import typing as tp

import sqlalchemy as sa
from sqlalchemy import orm as orm
from sqlalchemy.ext import asyncio as sa_asyncio

from app.models import users as user_models
from app.repositories import base as base_repository


class UserRepository(base_repository.BaseRepository[user_models.User]):
    """Repository for User operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(user_models.User, db)

    async def get_by_username(self, username: str) -> user_models.User | None:
        """Get user by username"""
        stmt = sa.select(user_models.User).where(user_models.User.username == username)
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(user_models.User | None, obj)

    async def get_by_email(self, email: str) -> user_models.User | None:
        """Get user by email"""
        stmt = sa.select(user_models.User).where(user_models.User.email == email)
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(user_models.User | None, obj)

    async def get_by_username_or_email(self, username_or_email: str) -> user_models.User | None:
        """Get user by username or email"""
        stmt = sa.select(user_models.User).where(
            sa.or_(
                user_models.User.username == username_or_email,
                user_models.User.email == username_or_email,
            )
        )
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(user_models.User | None, obj)

    async def get_with_login_data(self, user_id: int) -> user_models.User | None:
        """Get user with login data"""
        stmt = (
            sa.select(user_models.User)
            .options(orm.joinedload(user_models.User.login_data))
            .where(user_models.User.id == user_id)
        )
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(user_models.User | None, obj)

    async def get_with_profile(self, user_id: int) -> user_models.User | None:
        """Get user with teacher/student profile"""
        stmt = (
            sa.select(user_models.User)
            .options(
                orm.joinedload(user_models.User.teacher),
                orm.joinedload(user_models.User.student),
            )
            .where(user_models.User.id == user_id)
        )
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(user_models.User | None, obj)

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> list[user_models.User]:
        """Get all active users"""
        stmt = (
            sa.select(user_models.User)
            .where(user_models.User.is_active)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[user_models.User], items)


class LoginDataRepository(base_repository.BaseRepository[user_models.LoginData]):
    """Repository for LoginData operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(user_models.LoginData, db)

    async def get_by_user_id(self, user_id: int) -> user_models.LoginData | None:
        """Get login data by user ID"""
        stmt = sa.select(user_models.LoginData).where(user_models.LoginData.user_id == user_id)
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(user_models.LoginData | None, obj)

    async def create_for_user(self, user_id: int, hashed_password: str) -> user_models.LoginData:
        """Create login data for user"""
        return await self.create({"user_id": user_id, "hashed_password": hashed_password})

    async def update_password(
        self, user_id: int, hashed_password: str
    ) -> user_models.LoginData | None:
        """Update user password"""
        login_data = await self.get_by_user_id(user_id)
        if not login_data:
            return None
        return await self.update(login_data.id, {"hashed_password": hashed_password})


class TeacherRepository(base_repository.BaseRepository[user_models.Teacher]):
    """Repository for Teacher operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(user_models.Teacher, db)

    async def get_by_user_id(self, user_id: int) -> user_models.Teacher | None:
        """Get teacher by user ID"""
        stmt = sa.select(user_models.Teacher).where(user_models.Teacher.user_id == user_id)
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(user_models.Teacher | None, obj)

    async def get_with_user(self, teacher_id: int) -> user_models.Teacher | None:
        """Get teacher with user data"""
        stmt = (
            sa.select(user_models.Teacher)
            .options(orm.joinedload(user_models.Teacher.user))
            .where(user_models.Teacher.id == teacher_id)
        )
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(user_models.Teacher | None, obj)

    async def get_by_subject(
        self, subject: str, skip: int = 0, limit: int = 100
    ) -> list[user_models.Teacher]:
        """Get teachers by subject specialization"""
        stmt = (
            sa.select(user_models.Teacher)
            .where(user_models.Teacher.subject_specialization == subject)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[user_models.Teacher], items)


class StudentRepository(base_repository.BaseRepository[user_models.Student]):
    """Repository for Student operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(user_models.Student, db)

    async def get_by_user_id(self, user_id: int) -> user_models.Student | None:
        """Get student by user ID"""
        stmt = sa.select(user_models.Student).where(user_models.Student.user_id == user_id)
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(user_models.Student | None, obj)

    async def get_with_user(self, student_id: int) -> user_models.Student | None:
        """Get student with user data"""
        stmt = (
            sa.select(user_models.Student)
            .options(orm.joinedload(user_models.Student.user))
            .where(user_models.Student.id == student_id)
        )
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(user_models.Student | None, obj)

    async def get_by_grade_level(
        self, grade_level: int, skip: int = 0, limit: int = 100
    ) -> list[user_models.Student]:
        """Get students by grade level"""
        stmt = (
            sa.select(user_models.Student)
            .where(user_models.Student.grade_level == grade_level)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[user_models.Student], items)
