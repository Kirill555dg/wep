"""add composite indexes for chat messages

Revision ID: 184c91ba4c8d
Revises: 34aedd258882
Create Date: 2025-12-22 14:23:36.503608

"""

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "184c91ba4c8d"
down_revision: str | None = "34aedd258882"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_messages_chat_id_id
        ON messages (chat_id, id)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_messages_chat_id_created_at
        ON messages (chat_id, created_at)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_messages_chat_id_created_at")
    op.execute("DROP INDEX IF EXISTS ix_messages_chat_id_id")
