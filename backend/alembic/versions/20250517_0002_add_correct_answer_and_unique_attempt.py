"""add correct_answer to questions, unique active attempt index

Revision ID: 0002correct
Revises: 0001init
Create Date: 2025-05-17
"""

import sqlalchemy as sa
from alembic import op

revision = "0002correct"
down_revision = "0001init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("correct_answer", sa.Text, nullable=True))
    op.create_index(
        "uix_attempts_one_active_per_user_test",
        "attempts",
        ["user_id", "test_id"],
        unique=True,
        postgresql_where=sa.text("status = 'IN_PROGRESS'"),
    )


def downgrade() -> None:
    op.drop_index("uix_attempts_one_active_per_user_test", table_name="attempts")
    op.drop_column("questions", "correct_answer")
