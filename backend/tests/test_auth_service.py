"""
Tests for AuthService
"""

import pytest

from app.core import security as core_security
from app.repositories import user as user_repository
from app.schemas import users as user_schemas
from app.services import auth as auth_service_module
from app.services import exceptions as service_exceptions


pytestmark = pytest.mark.anyio


async def test_register_user(db_session):
    auth_service = auth_service_module.AuthService(db_session)

    user_data = user_schemas.UserCreate(
        email="john@example.com",
        password="TestPassword123!",
        first_name="John",
        last_name="Doe",
        middle_name="Smith",
    )

    user = await auth_service.register_user(user_data)

    assert user.email == "john@example.com"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.is_active is True

    login_repo = user_repository.LoginDataRepository(db_session)
    login_data = await login_repo.get_by_user_id(user.id)
    assert login_data is not None
    assert login_data.hashed_password != "TestPassword123!"


async def test_register_duplicate_email(db_session):
    auth_service = auth_service_module.AuthService(db_session)

    user_data = user_schemas.UserCreate(
        email="duplicate@example.com",
        password="Password123!",
        first_name="First",
        last_name="User",
    )
    await auth_service.register_user(user_data)

    duplicate_data = user_schemas.UserCreate(
        email="duplicate@example.com",
        password="DifferentPass123!",
        first_name="Second",
        last_name="User",
    )
    with pytest.raises(service_exceptions.ServiceError) as exc_info:
        await auth_service.register_user(duplicate_data)

    assert exc_info.value.code == "email_taken"


async def test_authenticate_success(db_session):
    auth_service = auth_service_module.AuthService(db_session)

    user_data = user_schemas.UserCreate(
        email="auth@example.com",
        password="AuthPassword123!",
        first_name="Auth",
        last_name="Test",
    )
    await auth_service.register_user(user_data)

    login_data = user_schemas.UserLogin(username_or_email="auth@example.com", password="AuthPassword123!")
    token = await auth_service.authenticate(login_data)

    assert token is not None
    assert token.access_token is not None
    assert token.token_type == "bearer"
    payload = core_security.decode_access_token(token.access_token)
    assert payload is not None
    assert payload.get("sub") is not None


async def test_authenticate_wrong_password(db_session):
    auth_service = auth_service_module.AuthService(db_session)

    user_data = user_schemas.UserCreate(
        email="wrongpass@example.com",
        password="CorrectPassword123!",
        first_name="Wrong",
        last_name="Pass",
    )
    await auth_service.register_user(user_data)

    login_data = user_schemas.UserLogin(username_or_email="wrongpass@example.com", password="WrongPassword123!")
    token = await auth_service.authenticate(login_data)

    assert token is None


async def test_authenticate_nonexistent_user(db_session):
    auth_service = auth_service_module.AuthService(db_session)

    login_data = user_schemas.UserLogin(username_or_email="nonexistent@example.com", password="SomePassword123!")
    token = await auth_service.authenticate(login_data)

    assert token is None
