"""remove role from users, drop teachers/students, add expires_at to attempts

Revision ID: 0003role
Revises: 0002correct
Create Date: 2025-05-17
"""

import sqlalchemy as sa
from alembic import op

revision = "0003role"
down_revision = "0002correct"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("users", "role")
    op.drop_table("students")
    op.drop_table("teachers")
    op.add_column("attempts", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("attempts", "expires_at")
    op.create_table(
        "teachers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("subject_specialization", sa.String(255), nullable=True),
        sa.Column("years_of_experience", sa.Integer, default=0),
        sa.Column("rating", sa.Integer, default=0),
    )
    op.create_table(
        "students",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("grade_level", sa.Integer, nullable=True),
        sa.Column("student_id_number", sa.String(50), unique=True, nullable=True),
        sa.Column("enrollment_date", sa.DateTime(timezone=True), nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("role", sa.String(20), nullable=False, server_default="student"),
    )
