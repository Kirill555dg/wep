"""
FastAPI dependencies for dependency injection
"""

import dataclasses as dc

import fastapi
from fastapi import security as fastapi_security
from fastapi import status as http_status
from sqlalchemy.ext import asyncio as sa_asyncio

from app.core import security as core_security
from app.db import session as db_session
from app.models import users as user_models
from app.repositories import homework as homework_repo
from app.repositories import user as user_repo
from app.services import auth as auth_service
from app.services import classroom as classroom_service
from app.services import homework as homework_service
from app.services import lesson as lesson_service
from app.services import problem as problem_service
from app.services import result as result_service
from app.services import chat as chat_service
from app.services import theory as theory_service
from app.services import testing as testing_service

# Security
security = fastapi_security.HTTPBearer()

@dc.dataclass(frozen=True, slots=True)
class TokenContext:
    user_id: int
    role: str


def get_current_user_id(
    credentials: fastapi_security.HTTPAuthorizationCredentials = fastapi.Depends(security),
) -> TokenContext:
    """
    Extract and validate JWT token, return user ID

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    payload = core_security.decode_access_token(token)

    if not payload:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = payload.get("role")
    if role is None:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail={"code": "token_missing_role", "message": "Token missing role"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return TokenContext(user_id=int(user_id), role=str(role))
    except ValueError:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: TokenContext = fastapi.Depends(get_current_user_id),
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> user_models.User:
    """
    Get current authenticated user from database

    Raises:
        HTTPException: If user not found or inactive
    """
    user_repository = user_repo.UserRepository(db)
    user = await user_repository.get_by_id(token.user_id)

    if not user:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if token.role != user.role:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "role_changed",
                "message": "Role changed, please re-authenticate",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_teacher(
    current_user: user_models.User = fastapi.Depends(get_current_user),
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> user_models.User:
    """
    Verify current user is a teacher

    Raises:
        HTTPException: If user is not a teacher
    """
    if current_user.role != "teacher":
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access this resource",
        )

    teacher_repository = user_repo.TeacherRepository(db)
    teacher = await teacher_repository.get_by_user_id(current_user.id)

    if not teacher:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Teacher profile not found",
        )

    return current_user


async def get_current_student(
    current_user: user_models.User = fastapi.Depends(get_current_user),
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> user_models.User:
    """
    Verify current user is a student

    Raises:
        HTTPException: If user is not a student
    """
    if current_user.role != "student":
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only students can access this resource",
        )

    student_repository = user_repo.StudentRepository(db)
    student = await student_repository.get_by_user_id(current_user.id)

    if not student:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Student profile not found",
        )

    return current_user


# Service dependencies
def get_auth_service(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> auth_service.AuthService:
    """Get AuthService instance"""
    return auth_service.AuthService(db)


def get_classroom_service(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> classroom_service.ClassroomService:
    """Get ClassroomService instance"""
    return classroom_service.ClassroomService(db)


def get_lesson_service(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> lesson_service.LessonService:
    """Get LessonService instance"""
    return lesson_service.LessonService(db)


def get_homework_service(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> homework_service.HomeworkService:
    """Get HomeworkService instance"""
    return homework_service.HomeworkService(db)


def get_testing_service(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> testing_service.TestingService:
    """Get TestingService instance"""
    return testing_service.TestingService(db)


def get_result_service(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> result_service.ResultService:
    """Get ResultService instance"""
    return result_service.ResultService(db)


def get_problem_service(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> problem_service.ProblemService:
    """Get ProblemService instance"""
    return problem_service.ProblemService(homework_repo.ProblemRepository(db))


def get_theory_service(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> theory_service.TheoryService:
    """Get TheoryService instance"""
    return theory_service.TheoryService(db)


def get_chat_service(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> chat_service.ChatService:
    """Get ChatService instance"""
    return chat_service.ChatService(db)
