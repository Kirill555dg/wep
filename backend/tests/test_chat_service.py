"""
Tests for ChatService.
"""

import pytest

from app.domain import errors as domain_errors
from app.repositories import user as user_repository
from app.schemas import classrooms as classroom_schemas
from app.schemas import communication as communication_schemas
from app.schemas import users as user_schemas
from app.services import auth as auth_service_module
from app.services import chat as chat_service_module
from app.services import classroom as classroom_service_module


pytestmark = pytest.mark.anyio


async def test_chat_service_teacher_can_post_and_list(db_session):
    auth_service = auth_service_module.AuthService(db_session)
    classroom_service = classroom_service_module.ClassroomService(db_session)
    chat_service = chat_service_module.ChatService(db_session)
    user_repo = user_repository.UserRepository(db_session)

    teacher_resp = await auth_service.register_user(
        user_schemas.UserCreate(
            email="chat_teacher@example.com",
            password="TeacherPass123!",
            first_name="Teach",
            last_name="Er",
            role="teacher",
        )
    )
    teacher = await user_repo.get_by_id(teacher_resp.id)
    assert teacher is not None

    created_classroom = await classroom_service.create_classroom(
        classroom_schemas.ClassroomCreate(name="Chat class", subject="Math", grade_level=7),
        teacher.id,
    )
    assert created_classroom.invite_code is not None

    posted = await chat_service.post_message(
        created_classroom.id,
        user=teacher,
        payload=communication_schemas.MessageCreate(content="Hello class!"),
    )
    assert posted.content == "Hello class!"
    assert posted.sender is not None
    assert posted.sender.id == teacher.id

    messages = await chat_service.list_messages(created_classroom.id, user=teacher, skip=0, limit=100)
    assert [m.content for m in messages] == ["Hello class!"]

    # Student member can access and post too.
    student_resp = await auth_service.register_user(
        user_schemas.UserCreate(
            email="chat_student@example.com",
            password="StudentPass123!",
            first_name="Stud",
            last_name="Ent",
            role="student",
        )
    )
    student = await user_repo.get_by_id(student_resp.id)
    assert student is not None

    await classroom_service.join_classroom(
        classroom_schemas.JoinClassroomRequest(invite_code=created_classroom.invite_code),
        student.id,
    )

    await chat_service.post_message(
        created_classroom.id,
        user=student,
        payload=communication_schemas.MessageCreate(content="Hi teacher!"),
    )

    messages = await chat_service.list_messages(created_classroom.id, user=student, skip=0, limit=100)
    assert [m.content for m in messages] == ["Hello class!", "Hi teacher!"]


async def test_chat_service_rejects_non_member_student(db_session):
    auth_service = auth_service_module.AuthService(db_session)
    classroom_service = classroom_service_module.ClassroomService(db_session)
    chat_service = chat_service_module.ChatService(db_session)
    user_repo = user_repository.UserRepository(db_session)

    teacher_resp = await auth_service.register_user(
        user_schemas.UserCreate(
            email="chat_teacher2@example.com",
            password="TeacherPass123!",
            first_name="Teach",
            last_name="Er",
            role="teacher",
        )
    )
    teacher = await user_repo.get_by_id(teacher_resp.id)
    assert teacher is not None

    created_classroom = await classroom_service.create_classroom(
        classroom_schemas.ClassroomCreate(name="Chat class 2", subject="Math", grade_level=7),
        teacher.id,
    )

    outsider_resp = await auth_service.register_user(
        user_schemas.UserCreate(
            email="chat_outsider@example.com",
            password="StudentPass123!",
            first_name="Out",
            last_name="Side",
            role="student",
        )
    )
    outsider = await user_repo.get_by_id(outsider_resp.id)
    assert outsider is not None

    with pytest.raises(domain_errors.ForbiddenError):
        await chat_service.list_messages(created_classroom.id, user=outsider, skip=0, limit=10)

