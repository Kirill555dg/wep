"""
Problem models: Problem, ProblemImage
"""

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app.core import datetime_extensions as dte
from app.db import session as db_session


class Problem(db_session.Base):
    """Problem/Task/Question"""

    __tablename__ = "problems"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=False)  # текст задачи
    problem_type = sa.Column(sa.String(50), nullable=False)
    difficulty = sa.Column(sa.Integer, default=1, nullable=False)
    correct_answer = sa.Column(sa.Text, nullable=True)  # правильный ответ (может быть JSON для вариантов)
    explanation = sa.Column(sa.Text, nullable=True)  # объяснение решения
    hints = sa.Column(sa.Text, nullable=True)  # подсказки (может быть JSON массив)
    is_published = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=dte.utc_now,
        onupdate=dte.utc_now,
        nullable=False,
    )

    # Relationships
    homework_problems = orm.relationship(
        "HomeworkProblem", back_populates="problem", cascade="all, delete-orphan"
    )
    images = orm.relationship("ProblemImage", back_populates="problem", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Problem(id={self.id}, title='{self.title}', type='{self.problem_type}')>"


class ProblemImage(db_session.Base):
    """Images attached to problems"""

    __tablename__ = "problem_images"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    problem_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
    )
    caption = sa.Column(sa.String(255), nullable=True)
    order_number = sa.Column(sa.Integer, default=0, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    # Relationships
    problem = orm.relationship("Problem", back_populates="images")
    file = orm.relationship("File")

    def __repr__(self) -> str:
        return f"<ProblemImage(id={self.id}, problem_id={self.problem_id})>"
