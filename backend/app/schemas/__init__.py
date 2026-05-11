"""
Pydantic schemas (DTOs - Data Transfer Objects)
"""

from app.schemas import classrooms as classrooms
from app.schemas import homework as homework
from app.schemas import lessons as lessons
from app.schemas import users as users

ClassroomBase = classrooms.ClassroomBase
ClassroomCreate = classrooms.ClassroomCreate
ClassroomDetailResponse = classrooms.ClassroomDetailResponse
ClassroomResponse = classrooms.ClassroomResponse
ClassroomUpdate = classrooms.ClassroomUpdate
InviteCreate = classrooms.InviteCreate
InviteResponse = classrooms.InviteResponse
JoinClassroomRequest = classrooms.JoinClassroomRequest

HomeworkBase = homework.HomeworkBase
HomeworkCreate = homework.HomeworkCreate
HomeworkDetailResponse = homework.HomeworkDetailResponse
HomeworkResponse = homework.HomeworkResponse
HomeworkUpdate = homework.HomeworkUpdate
ProblemBase = homework.ProblemBase
ProblemCreate = homework.ProblemCreate
ProblemFullResponse = homework.ProblemFullResponse
ProblemResponse = homework.ProblemResponse
ProblemUpdate = homework.ProblemUpdate
StatisticsBase = homework.StatisticsBase
StatisticsCreate = homework.StatisticsCreate
StatisticsResponse = homework.StatisticsResponse
StatisticsUpdate = homework.StatisticsUpdate
AnswerSubmit = homework.AnswerSubmit

LessonBase = lessons.LessonBase
LessonCreate = lessons.LessonCreate
LessonDetailResponse = lessons.LessonDetailResponse
LessonResponse = lessons.LessonResponse
LessonUpdate = lessons.LessonUpdate
TheoryMaterialBase = lessons.TheoryMaterialBase
TheoryMaterialCreate = lessons.TheoryMaterialCreate
TheoryMaterialResponse = lessons.TheoryMaterialResponse
TheoryMaterialUpdate = lessons.TheoryMaterialUpdate

LoginRequest = users.LoginRequest
UserLogin = users.UserLogin
StudentBase = users.StudentBase
StudentCreate = users.StudentCreate
StudentResponse = users.StudentResponse
StudentUpdate = users.StudentUpdate
TeacherBase = users.TeacherBase
TeacherCreate = users.TeacherCreate
TeacherResponse = users.TeacherResponse
TeacherUpdate = users.TeacherUpdate
TokenResponse = users.TokenResponse
UserBase = users.UserBase
UserCreate = users.UserCreate
UserInDB = users.UserInDB
UserRole = users.UserRole
UserResponse = users.UserResponse
UserUpdate = users.UserUpdate

__all__ = [
    # Users
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "TeacherBase",
    "TeacherCreate",
    "TeacherUpdate",
    "TeacherResponse",
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "LoginRequest",
    "UserLogin",
    "TokenResponse",
    "UserRole",
    # Classrooms
    "ClassroomBase",
    "ClassroomCreate",
    "ClassroomUpdate",
    "ClassroomResponse",
    "ClassroomDetailResponse",
    "InviteCreate",
    "InviteResponse",
    "JoinClassroomRequest",
    # Lessons
    "LessonBase",
    "LessonCreate",
    "LessonUpdate",
    "LessonResponse",
    "LessonDetailResponse",
    "TheoryMaterialBase",
    "TheoryMaterialCreate",
    "TheoryMaterialUpdate",
    "TheoryMaterialResponse",
    # Homework
    "HomeworkBase",
    "HomeworkCreate",
    "HomeworkUpdate",
    "HomeworkResponse",
    "HomeworkDetailResponse",
    "ProblemBase",
    "ProblemCreate",
    "ProblemUpdate",
    "ProblemResponse",
    "ProblemFullResponse",
    "StatisticsBase",
    "StatisticsCreate",
    "StatisticsUpdate",
    "StatisticsResponse",
    "AnswerSubmit",
]
