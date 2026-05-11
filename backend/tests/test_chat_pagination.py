"""
Tests for chat message pagination (tail/before_id).
"""

import pytest

from app.repositories import communication as communication_repository
from app.schemas import classrooms as classroom_schemas
from app.schemas import users as user_schemas
from app.services import auth as auth_service_module
from app.services import classroom as classroom_service_module


pytestmark = pytest.mark.anyio


async def test_message_repo_tail_and_before_id(db_session):
    auth_service = auth_service_module.AuthService(db_session)
    classroom_service = classroom_service_module.ClassroomService(db_session)

    teacher = await auth_service.register_user(
        user_schemas.UserCreate(
            email="chat_pagination_teacher@example.com",
            password="TeacherPass123!",
            first_name="Teach",
            last_name="Er",
            role="teacher",
        )
    )

    classroom = await classroom_service.create_classroom(
        classroom_schemas.ClassroomCreate(name="Paginated chat", subject="Math", grade_level=7),
        teacher.id,
    )

    chat_repo = communication_repository.ChatRepository(db_session)
    msg_repo = communication_repository.MessageRepository(db_session)

    chat = await chat_repo.create({"classroom_id": classroom.id, "name": "c", "is_active": True})

    # Create 5 messages
    ids: list[int] = []
    for i in range(1, 6):
        msg = await msg_repo.create(
            {
                "chat_id": chat.id,
                "sender_id": teacher.id,
                "content": f"m{i}",
                "is_edited": False,
                "is_deleted": False,
            }
        )
        ids.append(int(msg.id))

    # Tail should return last 2 (chronological)
    rows = await msg_repo.get_by_chat_with_sender(chat.id, limit=2, tail=True)
    assert [m.content for m, _u in rows] == ["m4", "m5"]

    # before_id should return items older than that id (chronological)
    rows = await msg_repo.get_by_chat_with_sender(chat.id, before_id=ids[3], limit=10)
    assert [m.content for m, _u in rows] == ["m1", "m2", "m3"]

