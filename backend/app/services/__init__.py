"""
Business logic services
"""

from app.services import auth as auth_service
from app.services import classroom as classroom_service
from app.services import homework as homework_service
from app.services import lesson as lesson_service
from app.services import problem as problem_service
from app.services import result as result_service
from app.services import testing as testing_service

AuthService = auth_service.AuthService
ClassroomService = classroom_service.ClassroomService
HomeworkService = homework_service.HomeworkService
LessonService = lesson_service.LessonService
ProblemService = problem_service.ProblemService
ResultService = result_service.ResultService
TestingService = testing_service.TestingService

__all__ = [
    "AuthService",
    "ClassroomService",
    "LessonService",
    "HomeworkService",
    "TestingService",
    "ResultService",
    "ProblemService",
]
