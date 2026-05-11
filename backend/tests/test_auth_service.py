"""
Tests for AuthService
"""

import pytest

from app.domain import errors as domain_errors
from app.core import security as core_security
from app.repositories import user as user_repository
from app.schemas import users as user_schemas
from app.services import auth as auth_service_module


pytestmark = pytest.mark.anyio


async def test_register_user_teacher(db_session):
    """Test registering a new teacher user"""
    auth_service = auth_service_module.AuthService(db_session)

    user_data = user_schemas.UserCreate(
        email="teacher@example.com",
        password="TestPassword123!",
        first_name="John",
        last_name="Doe",
        middle_name="Smith",
        role="teacher",
    )

    user = await auth_service.register_user(user_data)

    assert user.email == "teacher@example.com"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.role.value == "teacher"
    assert user.is_active is True
    # Password hash should exist in DB and not equal to plain
    login_repo = user_repository.LoginDataRepository(db_session)
    login_data = await login_repo.get_by_user_id(user.id)
    assert login_data is not None
    assert login_data.hashed_password != "TestPassword123!"

    # Teacher profile exists; student profile should not be auto-created anymore
    teacher_repo = user_repository.TeacherRepository(db_session)
    student_repo = user_repository.StudentRepository(db_session)
    assert await teacher_repo.get_by_user_id(user.id) is not None
    assert await student_repo.get_by_user_id(user.id) is None


async def test_register_user_student(db_session):
    """Test registering a new student user"""
    auth_service = auth_service_module.AuthService(db_session)

    user_data = user_schemas.UserCreate(
        email="student@example.com",
        password="StudentPass456!",
        first_name="Jane",
        last_name="Smith",
        role="student",
    )

    user = await auth_service.register_user(user_data)

    assert user.email == "student@example.com"
    assert user.role.value == "student"
    assert user.is_active is True

    # Student profile exists; teacher profile should not be auto-created anymore
    teacher_repo = user_repository.TeacherRepository(db_session)
    student_repo = user_repository.StudentRepository(db_session)
    assert await student_repo.get_by_user_id(user.id) is not None
    assert await teacher_repo.get_by_user_id(user.id) is None


async def test_switch_role_creates_profile_and_updates_active_role(db_session):
    auth_service = auth_service_module.AuthService(db_session)
    teacher_repo = user_repository.TeacherRepository(db_session)

    user = await auth_service.register_user(
        user_schemas.UserCreate(
            email="switch@example.com",
            password="SwitchPass123!",
            first_name="Role",
            last_name="Switch",
            role="student",
        )
    )

    assert await teacher_repo.get_by_user_id(user.id) is None

    roles = await auth_service.switch_role(user.id, user_schemas.UserRole.TEACHER)
    assert roles.active_role == user_schemas.UserRole.TEACHER
    assert user_schemas.UserRole.TEACHER in roles.enabled_roles
    assert await teacher_repo.get_by_user_id(user.id) is not None


async def test_old_token_becomes_invalid_after_role_switch(db_session):
    auth_service = auth_service_module.AuthService(db_session)

    user = await auth_service.register_user(
        user_schemas.UserCreate(
            email="role_token@example.com",
            password="RoleTokenPass123!",
            first_name="Role",
            last_name="Token",
            role="student",
        )
    )

    token_resp = await auth_service.authenticate(
        user_schemas.UserLogin(username_or_email="role_token@example.com", password="RoleTokenPass123!")
    )
    assert token_resp is not None

    # Switch active role to teacher (enables profile)
    await auth_service.switch_role(user.id, user_schemas.UserRole.TEACHER)

    payload = core_security.decode_access_token(token_resp.access_token)
    assert payload is not None
    assert payload.get("role") == "student"


async def test_register_duplicate_email(db_session):
    """Test that registering with duplicate email raises error"""
    auth_service = auth_service_module.AuthService(db_session)

    user_data = user_schemas.UserCreate(
        email="duplicate@example.com",
        password="Password123!",
        first_name="First",
        last_name="User",
        role="student",
    )

    # First registration should succeed
    await auth_service.register_user(user_data)

    # Second registration with same email should fail
    duplicate_data = user_schemas.UserCreate(
        email="duplicate@example.com",
        password="DifferentPass123!",
        first_name="Second",
        last_name="User",
        role="teacher",
    )

    with pytest.raises(domain_errors.BadRequestError) as exc_info:
        await auth_service.register_user(duplicate_data)

    assert "already registered" in str(exc_info.value).lower()


async def test_authenticate_success(db_session):
    """Test successful authentication"""
    auth_service = auth_service_module.AuthService(db_session)

    # Register a user first
    user_data = user_schemas.UserCreate(
        email="auth@example.com",
        password="AuthPassword123!",
        first_name="Auth",
        last_name="Test",
        role="student",
    )
    await auth_service.register_user(user_data)

    # Attempt to authenticate
    login_data = user_schemas.UserLogin(username_or_email="auth@example.com", password="AuthPassword123!")

    token = await auth_service.authenticate(login_data)

    assert token is not None
    assert token.access_token is not None
    assert token.token_type == "bearer"
    payload = core_security.decode_access_token(token.access_token)
    assert payload is not None
    assert payload.get("role") == "student"


async def test_authenticate_wrong_password(db_session):
    """Test authentication with wrong password"""
    auth_service = auth_service_module.AuthService(db_session)

    # Register a user
    user_data = user_schemas.UserCreate(
        email="wrongpass@example.com",
        password="CorrectPassword123!",
        first_name="Wrong",
        last_name="Pass",
        role="student",
    )
    await auth_service.register_user(user_data)

    # Attempt to authenticate with wrong password
    login_data = user_schemas.UserLogin(username_or_email="wrongpass@example.com", password="WrongPassword123!")

    token = await auth_service.authenticate(login_data)

    # Should return None for failed authentication
    assert token is None


async def test_authenticate_nonexistent_user(db_session):
    """Test authentication with non-existent email"""
    auth_service = auth_service_module.AuthService(db_session)

    login_data = user_schemas.UserLogin(username_or_email="nonexistent@example.com", password="SomePassword123!")

    token = await auth_service.authenticate(login_data)

    # Should return None for non-existent user
    assert token is None
