"""
SQLAlchemy ORM models
"""

from app.db import session as db_session
from app.models import test_constructor as test_constructor_models
from app.models import users as user_models

Base = db_session.Base

User = user_models.User
LoginData = user_models.LoginData
Teacher = user_models.Teacher
Student = user_models.Student

Test = test_constructor_models.Test
Question = test_constructor_models.Question
Option = test_constructor_models.Option
Tag = test_constructor_models.Tag
TestTag = test_constructor_models.TestTag
Attempt = test_constructor_models.Attempt
Answer = test_constructor_models.Answer
QuestionType = test_constructor_models.QuestionType
AttemptStatus = test_constructor_models.AttemptStatus

__all__ = [
    "Base",
    "User",
    "LoginData",
    "Teacher",
    "Student",
    "Test",
    "Question",
    "Option",
    "Tag",
    "TestTag",
    "Attempt",
    "Answer",
    "QuestionType",
    "AttemptStatus",
]
