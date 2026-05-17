"""init

Revision ID: 0001init
Revises:
Create Date: 2025-05-17
"""

from alembic import op
import sqlalchemy as sa

revision = "0001init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("middle_name", sa.String(100), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="student"),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "login_data",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "teachers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("subject_specialization", sa.String(255), nullable=True),
        sa.Column("years_of_experience", sa.Integer, server_default="0"),
        sa.Column("rating", sa.Integer, server_default="0"),
    )

    op.create_table(
        "students",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("grade_level", sa.Integer, nullable=True),
        sa.Column("student_id_number", sa.String(50), unique=True, nullable=True),
        sa.Column("enrollment_date", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "tests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("author_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_public", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("time_limit_minutes", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tests_author_id", "tests", ["author_id"])

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
    )
    op.create_index("ix_tags_slug", "tags", ["slug"])

    op.create_table(
        "test_tags",
        sa.Column("test_id", sa.Integer, sa.ForeignKey("tests.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )

    question_type = sa.Enum("SINGLE_CHOICE", "MULTIPLE_CHOICE", "TEXT", "ESSAY", name="questiontype")
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("test_id", sa.Integer, sa.ForeignKey("tests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_type", question_type, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("order_number", sa.Integer, nullable=False, server_default="0"),
        sa.Column("points", sa.Integer, nullable=False, server_default="1"),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("image_url", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_questions_test_id", "questions", ["test_id"])

    op.create_table(
        "options",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("question_id", sa.Integer, sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("is_correct", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("order_number", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_index("ix_options_question_id", "options", ["question_id"])

    attempt_status = sa.Enum("IN_PROGRESS", "COMPLETED", "EXPIRED", "ABANDONED", name="attemptstatus")
    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("test_id", sa.Integer, sa.ForeignKey("tests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Integer, nullable=True),
        sa.Column("max_score", sa.Integer, nullable=True),
        sa.Column("status", attempt_status, nullable=False, server_default="IN_PROGRESS"),
    )
    op.create_index("ix_attempts_test_id", "attempts", ["test_id"])
    op.create_index("ix_attempts_user_id", "attempts", ["user_id"])

    op.create_table(
        "answers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("attempt_id", sa.Integer, sa.ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.Integer, sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("selected_option_ids", sa.JSON, nullable=True),
        sa.Column("text_answer", sa.Text, nullable=True),
        sa.Column("is_correct", sa.Boolean, nullable=True),
        sa.Column("points_earned", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_answers_attempt_id", "answers", ["attempt_id"])
    op.create_index("ix_answers_question_id", "answers", ["question_id"])


def downgrade() -> None:
    op.drop_table("answers")
    op.drop_table("attempts")
    op.drop_table("options")
    op.drop_table("questions")
    op.drop_table("test_tags")
    op.drop_table("tags")
    op.drop_table("tests")
    op.drop_table("students")
    op.drop_table("teachers")
    op.drop_table("login_data")
    op.drop_table("users")
    sa.Enum(name="questiontype").drop(op.get_bind())
    sa.Enum(name="attemptstatus").drop(op.get_bind())
