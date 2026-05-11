"""
Classroom models: Classroom, StudentClassroom, Invite
"""

import enum

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app.core import datetime_extensions as dte
from app.db import session as db_session


class InviteStatus(str, enum.Enum):
    """Invite status enumeration"""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Classroom(db_session.Base):
    """Classroom/Class model"""

    __tablename__ = "classrooms"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    subject = sa.Column(sa.String(100), nullable=False)  # предмет (математика, физика и т.д.)
    grade_level = sa.Column(sa.Integer, nullable=True)  # класс (7, 8, 9 и т.д.)
    teacher_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("teachers.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    max_students = sa.Column(sa.Integer, default=30, nullable=True)
    invite_code = sa.Column(sa.String(50), unique=True, nullable=True)  # код для присоединения
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=dte.utc_now,
        onupdate=dte.utc_now,
        nullable=False,
    )

    # Relationships
    teacher = orm.relationship("Teacher", back_populates="classrooms")
    student_memberships = orm.relationship(
        "StudentClassroom", back_populates="classroom", cascade="all, delete-orphan"
    )
    lessons = orm.relationship("Lesson", back_populates="classroom", cascade="all, delete-orphan")
    invites = orm.relationship("Invite", back_populates="classroom", cascade="all, delete-orphan")
    chat = orm.relationship(
        "Chat", back_populates="classroom", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Classroom(id={self.id}, name='{self.name}', subject='{self.subject}')>"


class StudentClassroom(db_session.Base):
    """Many-to-many relationship between Students and Classrooms"""

    __tablename__ = "student_classrooms"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    student_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )
    classroom_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("classrooms.id", ondelete="CASCADE"),
        nullable=False,
    )
    enrolled_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)

    # Relationships
    student = orm.relationship("Student", back_populates="classroom_memberships")
    classroom = orm.relationship("Classroom", back_populates="student_memberships")

    def __repr__(self) -> str:
        return f"<StudentClassroom(student_id={self.student_id}, classroom_id={self.classroom_id})>"


class Invite(db_session.Base):
    """Invitation to join classroom"""

    __tablename__ = "invites"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    classroom_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("classrooms.id", ondelete="CASCADE"),
        nullable=False,
    )
    invite_code = sa.Column(sa.String(100), unique=True, nullable=False, index=True)
    max_uses = sa.Column(sa.Integer, default=1, nullable=True)  # максимальное количество использований
    uses_count = sa.Column(sa.Integer, default=0, nullable=False)
    status = sa.Column(sa.Enum(InviteStatus), default=InviteStatus.PENDING, nullable=False)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    # Relationships
    classroom = orm.relationship("Classroom", back_populates="invites")

    def __repr__(self) -> str:
        return f"<Invite(id={self.id}, code='{self.invite_code}', status='{self.status}')>"
