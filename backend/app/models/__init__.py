"""
SQLAlchemy ORM models
"""

from app.db import session as db_session
from app.models import classes as classes_models
from app.models import communication as communication_models
from app.models import files as file_models
from app.models import homework as homework_models
from app.models import lessons as lesson_models
from app.models import problems as problem_models
from app.models import theory as theory_models
from app.models import users as user_models

Base = db_session.Base

Classroom = classes_models.Classroom
Invite = classes_models.Invite
InviteStatus = classes_models.InviteStatus
StudentClassroom = classes_models.StudentClassroom

Chat = communication_models.Chat
Message = communication_models.Message

File = file_models.File

Homework = homework_models.Homework
HomeworkProblem = homework_models.HomeworkProblem
HomeworkStatus = homework_models.HomeworkStatus
Statistics = homework_models.Statistics

Lesson = lesson_models.Lesson
LessonMaterial = lesson_models.LessonMaterial

Problem = problem_models.Problem
ProblemImage = problem_models.ProblemImage

Subject = theory_models.Subject
Section = theory_models.Section
Subsection = theory_models.Subsection
TheoryMaterial = theory_models.TheoryMaterial
MaterialImage = theory_models.MaterialImage

User = user_models.User
LoginData = user_models.LoginData
Teacher = user_models.Teacher
Student = user_models.Student

__all__ = [
    # Base
    "Base",
    # Users
    "User",
    "LoginData",
    "Teacher",
    "Student",
    # Classes
    "Classroom",
    "StudentClassroom",
    "Invite",
    "InviteStatus",
    # Communication
    "Chat",
    "Message",
    # Lessons
    "Lesson",
    "LessonMaterial",
    # Theory
    "Subject",
    "Section",
    "Subsection",
    "TheoryMaterial",
    "MaterialImage",
    # Homework
    "Homework",
    "HomeworkProblem",
    "Statistics",
    "HomeworkStatus",
    # Problems
    "Problem",
    "ProblemImage",
    # Files
    "File",
]
