import sqlalchemy as sa
import sqlalchemy.orm as sqla_orm
from sqlalchemy.types import Enum as SAEnum

from app.core import datetime_extensions as dte
from app.db import session as db_session


class Test(db_session.Base):
    __tablename__ = "tests"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    author_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    is_public = sa.Column(sa.Boolean, default=False, nullable=False)
    time_limit_minutes = sa.Column(sa.Integer, nullable=True)
    attempt_limit = sa.Column(sa.Integer, nullable=True)  # None = unlimited
    track_time = sa.Column(sa.Boolean, default=True, nullable=False, server_default=sa.text('true'))
    completion_message = sa.Column(sa.Text, nullable=True)
    questions_count = sa.Column(sa.Integer, default=0, server_default='0', nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, onupdate=dte.utc_now, nullable=False)

    author = sqla_orm.relationship("User", foreign_keys=[author_id])
    questions = sqla_orm.relationship(
        "Question", back_populates="test", cascade="all, delete-orphan", order_by="Question.order_number"
    )
    test_tags = sqla_orm.relationship("TestTag", back_populates="test", cascade="all, delete-orphan")
    attempts = sqla_orm.relationship("Attempt", back_populates="test", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Test(id={self.id}, title='{self.title}', author_id={self.author_id})>"


class Question(db_session.Base):
    __tablename__ = "questions"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    test_id = sa.Column(sa.Integer, sa.ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True)
    question_type = sa.Column(sa.String(50), nullable=False)
    text = sa.Column(sa.Text, nullable=False)
    order_number = sa.Column(sa.Integer, default=0, nullable=False)
    points = sa.Column(sa.Integer, default=1, nullable=False)
    explanation = sa.Column(sa.Text, nullable=True)
    correct_answer = sa.Column(sa.Text, nullable=True)
    image_url = sa.Column(sa.String(512), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, onupdate=dte.utc_now, nullable=False)

    test = sqla_orm.relationship("Test", back_populates="questions")
    options = sqla_orm.relationship(
        "Option", back_populates="question", cascade="all, delete-orphan", order_by="Option.order_number"
    )
    answers = sqla_orm.relationship("Answer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, type='{self.question_type}', test_id={self.test_id})>"


class Option(db_session.Base):
    __tablename__ = "options"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    question_id = sa.Column(sa.Integer, sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    text = sa.Column(sa.Text, nullable=False)
    is_correct = sa.Column(sa.Boolean, default=False, nullable=False)
    order_number = sa.Column(sa.Integer, default=0, nullable=False)

    question = sqla_orm.relationship("Question", back_populates="options")

    def __repr__(self) -> str:
        return f"<Option(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>"


class Tag(db_session.Base):
    __tablename__ = "tags"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String(100), nullable=False, unique=True)
    slug = sa.Column(sa.String(100), nullable=False, unique=True, index=True)

    test_tags = sqla_orm.relationship("TestTag", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, slug='{self.slug}')>"


class TestTag(db_session.Base):
    __tablename__ = "test_tags"

    test_id = sa.Column(sa.Integer, sa.ForeignKey("tests.id", ondelete="CASCADE"), primary_key=True)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    test = sqla_orm.relationship("Test", back_populates="test_tags")
    tag = sqla_orm.relationship("Tag", back_populates="test_tags")

    def __repr__(self) -> str:
        return f"<TestTag(test_id={self.test_id}, tag_id={self.tag_id})>"


class Attempt(db_session.Base):
    __tablename__ = "attempts"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "test_id", name="uq_user_test_active_attempt"),
    )

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    test_id = sa.Column(sa.Integer, sa.ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    finished_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    score = sa.Column(sa.Integer, nullable=True)
    max_score = sa.Column(sa.Integer, nullable=True)
    status = sa.Column(sa.String(50), nullable=False)

    test = sqla_orm.relationship("Test", back_populates="attempts")
    user = sqla_orm.relationship("User", foreign_keys=[user_id])
    answers = sqla_orm.relationship("Answer", back_populates="attempt", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Attempt(id={self.id}, test_id={self.test_id}, user_id={self.user_id}, status='{self.status}')>"


class Answer(db_session.Base):
    __tablename__ = "answers"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    attempt_id = sa.Column(sa.Integer, sa.ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = sa.Column(sa.Integer, sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_option_ids = sa.Column(sa.JSON, nullable=True)
    text_answer = sa.Column(sa.Text, nullable=True)
    is_correct = sa.Column(sa.Boolean, nullable=True)
    points_earned = sa.Column(sa.Integer, nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    attempt = sqla_orm.relationship("Attempt", back_populates="answers")
    question = sqla_orm.relationship("Question", back_populates="answers")

    def __repr__(self) -> str:
        return f"<Answer(id={self.id}, attempt_id={self.attempt_id}, question_id={self.question_id})>"
