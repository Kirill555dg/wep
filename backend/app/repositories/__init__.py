"""
Data access repositories
"""

from app.repositories import base as base_repository
from app.repositories import user as user_repository

BaseRepository = base_repository.BaseRepository

UserRepository = user_repository.UserRepository
LoginDataRepository = user_repository.LoginDataRepository
TeacherRepository = user_repository.TeacherRepository
StudentRepository = user_repository.StudentRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "LoginDataRepository",
    "TeacherRepository",
    "StudentRepository",
]
