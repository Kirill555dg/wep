"""
Chat service (classroom chat).
"""

from sqlalchemy.ext import asyncio as sa_asyncio

from app.core import pagination as core_pagination
from app.models import users as user_models
from app.repositories import classroom as classroom_repository
from app.repositories import communication as communication_repository
from app.repositories import user as user_repository
from app.schemas import communication as communication_schemas
from app.services import access_control as access_control
from app.services import exceptions as service_exceptions


class ChatService:
    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.chat_repo = communication_repository.ChatRepository(db)
        self.message_repo = communication_repository.MessageRepository(db)
        self.classroom_repo = classroom_repository.ClassroomRepository(db)
        self.student_classroom_repo = classroom_repository.StudentClassroomRepository(db)
        self.teacher_repo = user_repository.TeacherRepository(db)
        self.student_repo = user_repository.StudentRepository(db)

    async def _require_chat_for_classroom(self, classroom_id: int) -> int:
        classroom = access_control.require_classroom(
            await self.classroom_repo.get_by_id(classroom_id),
            detail="Classroom not found",
        )

        chat = await self.chat_repo.get_by_classroom_id(classroom.id)
        if chat is None:
            chat = await self.chat_repo.create(
                {"classroom_id": classroom.id, "name": f"Classroom {classroom.id} chat", "is_active": True}
            )

        return int(chat.id)

    async def _require_user_can_access_classroom(
        self,
        *,
        classroom_id: int,
        user: user_models.User,
    ) -> None:
        classroom = access_control.require_classroom(
            await self.classroom_repo.get_by_id(classroom_id),
            detail="Classroom not found",
        )

        if user.role == "teacher":
            teacher = access_control.require_teacher_profile(
                await self.teacher_repo.get_by_user_id(user.id),
                detail="Only classroom owner can access chat",
            )
            access_control.require_teacher_owns_classroom(
                teacher=teacher,
                classroom=classroom,
                detail="Only classroom owner can access chat",
            )
            return

        if user.role == "student":
            student = await self.student_repo.get_by_user_id(user.id)
            if not student:
                raise service_exceptions.ServiceError(
                    "Only classroom members can access chat", code="forbidden",
                )
            if not await self.student_classroom_repo.is_student_in_classroom(student.id, classroom.id):
                raise service_exceptions.ServiceError(
                    "Only classroom members can access chat", code="forbidden",
                )
            return

        raise service_exceptions.ServiceError(
            "Only classroom members can access chat", code="forbidden",
        )

    async def require_access(self, classroom_id: int, *, user: user_models.User) -> None:
        """Ensure user can access classroom chat."""
        await self._require_user_can_access_classroom(classroom_id=classroom_id, user=user)

    async def list_messages(
        self,
        classroom_id: int,
        *,
        user: user_models.User,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
        before_id: int | None = None,
        tail: bool = False,
    ) -> list[communication_schemas.MessageResponse]:
        await self._require_user_can_access_classroom(classroom_id=classroom_id, user=user)
        chat_id = await self._require_chat_for_classroom(classroom_id)

        rows = await self.message_repo.get_by_chat_with_sender(
            chat_id,
            skip=skip,
            limit=limit,
            before_id=before_id,
            tail=tail,
        )
        result: list[communication_schemas.MessageResponse] = []
        for message, sender in rows:
            result.append(
                communication_schemas.MessageResponse(
                    id=message.id,
                    chat_id=message.chat_id,
                    sender_id=message.sender_id,
                    sender=communication_schemas.UserPublic.model_validate(sender),
                    content=message.content,
                    is_edited=message.is_edited,
                    is_deleted=message.is_deleted,
                    created_at=message.created_at,
                    updated_at=message.updated_at,
                )
            )
        return result

    async def count_messages(self, classroom_id: int, *, user: user_models.User) -> int:
        await self._require_user_can_access_classroom(classroom_id=classroom_id, user=user)
        chat_id = await self._require_chat_for_classroom(classroom_id)
        return await self.message_repo.count_by_chat(chat_id)

    async def post_message(
        self,
        classroom_id: int,
        *,
        user: user_models.User,
        payload: communication_schemas.MessageCreate,
    ) -> communication_schemas.MessageResponse:
        await self._require_user_can_access_classroom(classroom_id=classroom_id, user=user)
        chat_id = await self._require_chat_for_classroom(classroom_id)

        message = await self.message_repo.create(
            {
                "chat_id": chat_id,
                "sender_id": user.id,
                "content": payload.content,
                "is_edited": False,
                "is_deleted": False,
            }
        )

        # Sender is the current user.
        return communication_schemas.MessageResponse(
            id=message.id,
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            sender=communication_schemas.UserPublic.model_validate(user),
            content=message.content,
            is_edited=message.is_edited,
            is_deleted=message.is_deleted,
            created_at=message.created_at,
            updated_at=message.updated_at,
        )

