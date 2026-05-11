"""
Communication models: Chat, Message
"""

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app.core import datetime_extensions as dte
from app.db import session as db_session


class Chat(db_session.Base):
    """Chat for classroom"""

    __tablename__ = "chats"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    classroom_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("classrooms.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    name = sa.Column(sa.String(255), nullable=True)  # опционально, можно автоматически генерировать
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    # Relationships
    classroom = orm.relationship("Classroom", back_populates="chat")
    messages = orm.relationship("Message", back_populates="chat", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, classroom_id={self.classroom_id})>"


class Message(db_session.Base):
    """Message in chat"""

    __tablename__ = "messages"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    chat_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    content = sa.Column(sa.Text, nullable=False)
    is_edited = sa.Column(sa.Boolean, default=False, nullable=False)
    is_deleted = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False, index=True)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=dte.utc_now,
        onupdate=dte.utc_now,
        nullable=False,
    )

    # Relationships
    chat = orm.relationship("Chat", back_populates="messages")
    sender = orm.relationship("User")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, chat_id={self.chat_id}, sender_id={self.sender_id})>"
