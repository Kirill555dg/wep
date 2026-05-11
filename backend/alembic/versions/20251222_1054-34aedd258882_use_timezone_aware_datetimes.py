"""use timezone-aware datetimes

Revision ID: 34aedd258882
Revises: 68c303c89446
Create Date: 2025-12-22 10:54:47.078983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34aedd258882'
down_revision: str | None = '68c303c89446'
branch_labels: str | None = None
depends_on: str | None = None


def _get_column_data_type(
    connection: sa.engine.Connection,
    *,
    table_name: str,
    column_name: str,
) -> str | None:
    # Note: this checks only the current schema (public by default).
    stmt = sa.text(
        """
        SELECT c.data_type
        FROM information_schema.columns c
        WHERE c.table_schema = current_schema()
          AND c.table_name = :table_name
          AND c.column_name = :column_name
        """
    )
    value = connection.execute(stmt, {"table_name": table_name, "column_name": column_name}).scalar_one_or_none()
    return value if value is None else str(value)


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()
    columns: list[tuple[str, str]] = [
        ("users", "created_at"),
        ("users", "updated_at"),
        ("login_data", "last_login"),
        ("login_data", "created_at"),
        ("students", "enrollment_date"),
        ("problems", "created_at"),
        ("problems", "updated_at"),
        ("problem_images", "created_at"),
        ("lessons", "scheduled_at"),
        ("lessons", "created_at"),
        ("lessons", "updated_at"),
        ("lesson_materials", "added_at"),
        ("homeworks", "deadline"),
        ("homeworks", "created_at"),
        ("homeworks", "updated_at"),
        ("statistics", "submitted_at"),
        ("statistics", "graded_at"),
        ("statistics", "created_at"),
        ("statistics", "updated_at"),
        ("classrooms", "created_at"),
        ("classrooms", "updated_at"),
        ("student_classrooms", "enrolled_at"),
        ("invites", "expires_at"),
        ("invites", "created_at"),
        ("chats", "created_at"),
        ("messages", "created_at"),
        ("messages", "updated_at"),
        ("subjects", "created_at"),
        ("sections", "created_at"),
        ("subsections", "created_at"),
        ("theory_materials", "created_at"),
        ("theory_materials", "updated_at"),
        ("material_images", "created_at"),
        ("files", "created_at"),
    ]

    for table_name, column_name in columns:
        data_type = _get_column_data_type(connection, table_name=table_name, column_name=column_name)
        if data_type != "timestamp without time zone":
            # Already timestamptz (or column missing), do not alter.
            continue

        op.alter_column(
            table_name,
            column_name,
            type_=sa.DateTime(timezone=True),
            existing_type=sa.DateTime(),
            postgresql_using=f"{column_name} AT TIME ZONE 'UTC'",
        )


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    columns: list[tuple[str, str]] = [
        ("users", "created_at"),
        ("users", "updated_at"),
        ("login_data", "last_login"),
        ("login_data", "created_at"),
        ("students", "enrollment_date"),
        ("problems", "created_at"),
        ("problems", "updated_at"),
        ("problem_images", "created_at"),
        ("lessons", "scheduled_at"),
        ("lessons", "created_at"),
        ("lessons", "updated_at"),
        ("lesson_materials", "added_at"),
        ("homeworks", "deadline"),
        ("homeworks", "created_at"),
        ("homeworks", "updated_at"),
        ("statistics", "submitted_at"),
        ("statistics", "graded_at"),
        ("statistics", "created_at"),
        ("statistics", "updated_at"),
        ("classrooms", "created_at"),
        ("classrooms", "updated_at"),
        ("student_classrooms", "enrolled_at"),
        ("invites", "expires_at"),
        ("invites", "created_at"),
        ("chats", "created_at"),
        ("messages", "created_at"),
        ("messages", "updated_at"),
        ("subjects", "created_at"),
        ("sections", "created_at"),
        ("subsections", "created_at"),
        ("theory_materials", "created_at"),
        ("theory_materials", "updated_at"),
        ("material_images", "created_at"),
        ("files", "created_at"),
    ]

    for table_name, column_name in columns:
        data_type = _get_column_data_type(connection, table_name=table_name, column_name=column_name)
        if data_type != "timestamp with time zone":
            continue

        op.alter_column(
            table_name,
            column_name,
            type_=sa.DateTime(),
            existing_type=sa.DateTime(timezone=True),
            postgresql_using=f"{column_name} AT TIME ZONE 'UTC'",
        )
