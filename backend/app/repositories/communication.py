"""
Communication repositories (chat/messages).
"""

import typing as tp

import sqlalchemy as sa
from sqlalchemy.ext import asyncio as sa_asyncio

from app.models import communication as communication_models
from app.models import users as user_models
from app.repositories import base as base_repository


class ChatRepository(base_repository.BaseRepository[communication_models.Chat]):
    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(communication_models.Chat, db)

    async def get_by_classroom_id(self, classroom_id: int) -> communication_models.Chat | None:
        stmt = sa.select(communication_models.Chat).where(communication_models.Chat.classroom_id == classroom_id)
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(communication_models.Chat | None, obj)


class MessageRepository(base_repository.BaseRepository[communication_models.Message]):
    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(communication_models.Message, db)

    async def get_by_chat(
        self,
        chat_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[communication_models.Message]:
        stmt = (
            sa.select(communication_models.Message)
            .where(communication_models.Message.chat_id == chat_id, ~communication_models.Message.is_deleted)
            .order_by(communication_models.Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[communication_models.Message], items)

    async def get_by_chat_with_sender(
        self,
        chat_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        before_id: int | None = None,
        tail: bool = False,
    ) -> list[tuple[communication_models.Message, user_models.User]]:
        if before_id is not None or tail:
            # Cursor mode: fetch latest messages (tail) or older than before_id.
            conditions: list[tp.Any] = [
                communication_models.Message.chat_id == chat_id,
                ~communication_models.Message.is_deleted,
            ]
            if before_id is not None:
                conditions.append(communication_models.Message.id < before_id)

            stmt = (
                sa.select(communication_models.Message, user_models.User)
                .join(user_models.User, user_models.User.id == communication_models.Message.sender_id)
                .where(*conditions)
                .order_by(communication_models.Message.id.desc())
                .limit(limit)
            )
        else:
            # Offset pagination (legacy): stable order for skip/limit.
            stmt = (
                sa.select(communication_models.Message, user_models.User)
                .join(user_models.User, user_models.User.id == communication_models.Message.sender_id)
                .where(
                    communication_models.Message.chat_id == chat_id,
                    ~communication_models.Message.is_deleted,
                )
                .order_by(communication_models.Message.created_at.asc())
                .offset(skip)
                .limit(limit)
            )
        result = await self.db.execute(stmt)
        rows = list(result.all())
        if before_id is not None or tail:
            rows.reverse()  # Return chronological order for UI.
        return tp.cast(list[tuple[communication_models.Message, user_models.User]], rows)

    async def count_by_chat(self, chat_id: int) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(communication_models.Message)
            .where(
                communication_models.Message.chat_id == chat_id,
                ~communication_models.Message.is_deleted,
            )
        )
        value = (await self.db.execute(stmt)).scalar_one()
        return tp.cast(int, value)

