"""
Data access repositories
"""

from app.repositories import base as base_repository
from app.repositories import classroom as classroom_repository
from app.repositories import homework as homework_repository
from app.repositories import lesson as lesson_repository
from app.repositories import user as user_repository

BaseRepository = base_repository.BaseRepository

UserRepository = user_repository.UserRepository
LoginDataRepository = user_repository.LoginDataRepository
TeacherRepository = user_repository.TeacherRepository
StudentRepository = user_repository.StudentRepository

ClassroomRepository = classroom_repository.ClassroomRepository
StudentClassroomRepository = classroom_repository.StudentClassroomRepository
InviteRepository = classroom_repository.InviteRepository

LessonRepository = lesson_repository.LessonRepository
LessonMaterialRepository = lesson_repository.LessonMaterialRepository
TheoryMaterialRepository = lesson_repository.TheoryMaterialRepository
SubjectRepository = lesson_repository.SubjectRepository

HomeworkRepository = homework_repository.HomeworkRepository
HomeworkProblemRepository = homework_repository.HomeworkProblemRepository
ProblemRepository = homework_repository.ProblemRepository
StatisticsRepository = homework_repository.StatisticsRepository

__all__ = [
    # Base
    "BaseRepository",
    # Users
    "UserRepository",
    "LoginDataRepository",
    "TeacherRepository",
    "StudentRepository",
    # Classrooms
    "ClassroomRepository",
    "StudentClassroomRepository",
    "InviteRepository",
    # Lessons
    "LessonRepository",
    "LessonMaterialRepository",
    "TheoryMaterialRepository",
    "SubjectRepository",
    # Homework
    "HomeworkRepository",
    "HomeworkProblemRepository",
    "ProblemRepository",
    "StatisticsRepository",
]
