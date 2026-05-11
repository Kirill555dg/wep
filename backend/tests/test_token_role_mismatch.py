"""
Tests for token role mismatch behavior.
"""

import pytest

import fastapi

from app.api import dependencies as deps
from app.schemas import users as user_schemas
from app.services import auth as auth_service_module


pytestmark = pytest.mark.anyio


async def test_get_current_user_rejects_role_mismatch(db_session):
    auth_service = auth_service_module.AuthService(db_session)

    user = await auth_service.register_user(
        user_schemas.UserCreate(
            email="mismatch@example.com",
            password="MismatchPass123!",
            first_name="Mis",
            last_name="Match",
            role="student",
        )
    )

    # User switches role in DB.
    await auth_service.switch_role(user.id, user_schemas.UserRole.TEACHER)

    with pytest.raises(fastapi.HTTPException) as exc:
        await deps.get_current_user(token=deps.TokenContext(user_id=user.id, role="student"), db=db_session)

    assert exc.value.status_code == 401

