"""
Lesson models: Lesson, LessonMaterial
"""

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app.core import datetime_extensions as dte
from app.db import session as db_session


class Lesson(db_session.Base):
    """Lesson in classroom"""

    __tablename__ = "lessons"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    classroom_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("classrooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    order_number = sa.Column(sa.Integer, nullable=True)  # порядковый номер урока в курсе
    is_published = sa.Column(sa.Boolean, default=False, nullable=False)
    scheduled_at = sa.Column(sa.DateTime(timezone=True), nullable=True)  # когда урок запланирован
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=dte.utc_now,
        onupdate=dte.utc_now,
        nullable=False,
    )

    # Relationships
    classroom = orm.relationship("Classroom", back_populates="lessons")
    homeworks = orm.relationship("Homework", back_populates="lesson", cascade="all, delete-orphan")
    lesson_materials = orm.relationship(
        "LessonMaterial", back_populates="lesson", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Lesson(id={self.id}, title='{self.title}', classroom_id={self.classroom_id})>"


class LessonMaterial(db_session.Base):
    """Many-to-many relationship between Lessons and TheoryMaterials"""

    __tablename__ = "lesson_materials"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    lesson_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    theory_material_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("theory_materials.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_number = sa.Column(sa.Integer, default=0, nullable=False)  # порядок материала в уроке
    is_required = sa.Column(sa.Boolean, default=True, nullable=False)  # обязателен ли материал
    added_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    # Relationships
    lesson = orm.relationship("Lesson", back_populates="lesson_materials")
    theory_material = orm.relationship("TheoryMaterial", back_populates="lesson_materials")

    def __repr__(self) -> str:
        return f"<LessonMaterial(lesson_id={self.lesson_id}, theory_material_id={self.theory_material_id})>"
