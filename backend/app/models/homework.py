"""
Homework models: Homework, HomeworkProblem, Statistics
"""

import enum

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app.core import datetime_extensions as dte
from app.db import session as db_session


class HomeworkStatus(str, enum.Enum):
    """Homework status for students"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"


class Homework(db_session.Base):
    """Homework assignment"""

    __tablename__ = "homeworks"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    lesson_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    max_score = sa.Column(sa.Float, default=100.0, nullable=False)
    deadline = sa.Column(sa.DateTime(timezone=True), nullable=True)
    is_published = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=dte.utc_now,
        onupdate=dte.utc_now,
        nullable=False,
    )

    # Relationships
    lesson = orm.relationship("Lesson", back_populates="homeworks")
    homework_problems = orm.relationship(
        "HomeworkProblem", back_populates="homework", cascade="all, delete-orphan"
    )
    statistics = orm.relationship("Statistics", back_populates="homework", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Homework(id={self.id}, title='{self.title}', lesson_id={self.lesson_id})>"


class HomeworkProblem(db_session.Base):
    """Many-to-many relationship between Homework and Problems"""

    __tablename__ = "homework_problems"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    homework_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("homeworks.id", ondelete="CASCADE"),
        nullable=False,
    )
    problem_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_number = sa.Column(sa.Integer, default=0, nullable=False)  # порядок задачи в ДЗ
    points = sa.Column(sa.Float, default=10.0, nullable=False)  # баллы за задачу

    # Relationships
    homework = orm.relationship("Homework", back_populates="homework_problems")
    problem = orm.relationship("Problem", back_populates="homework_problems")

    def __repr__(self) -> str:
        return f"<HomeworkProblem(homework_id={self.homework_id}, problem_id={self.problem_id})>"


class Statistics(db_session.Base):
    """Student statistics for homework"""

    __tablename__ = "statistics"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    student_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    homework_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("homeworks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = sa.Column(sa.Enum(HomeworkStatus), default=HomeworkStatus.NOT_STARTED, nullable=False)
    score = sa.Column(sa.Float, default=0.0, nullable=False)  # набранные баллы
    max_score = sa.Column(sa.Float, nullable=False)  # максимально возможные баллы
    attempts_count = sa.Column(sa.Integer, default=0, nullable=False)  # количество попыток
    time_spent_minutes = sa.Column(sa.Integer, default=0, nullable=False)  # затраченное время
    submitted_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    graded_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    feedback = sa.Column(sa.Text, nullable=True)  # обратная связь от преподавателя
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=dte.utc_now,
        onupdate=dte.utc_now,
        nullable=False,
    )

    # Relationships
    student = orm.relationship("Student", back_populates="statistics")
    homework = orm.relationship("Homework", back_populates="statistics")

    def __repr__(self) -> str:
        return f"<Statistics(id={self.id}, student_id={self.student_id}, homework_id={self.homework_id}, status='{self.status}')>"
