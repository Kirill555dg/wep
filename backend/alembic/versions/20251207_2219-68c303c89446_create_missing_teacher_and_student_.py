"""create missing teacher/student profiles for existing users

Revision ID: 68c303c89446
Revises: 765d7038a0e6
Create Date: 2025-12-07 22:19:02.185915

"""

import typing as tp

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "68c303c89446"
down_revision: tp.Union[str, tp.Sequence[str], None] = "765d7038a0e6"
branch_labels: tp.Union[str, tp.Sequence[str], None] = None
depends_on: tp.Union[str, tp.Sequence[str], None] = None


def upgrade() -> None:
    """
    Create missing profiles for existing users based on their active role.

    Note: users can enable the other role later via the API (role switching).
    """
    # Create teacher profiles for users with active role = teacher.
    op.execute("""
        INSERT INTO teachers (user_id, bio, subject_specialization, years_of_experience, rating)
        SELECT u.id, NULL, NULL, 0, 0
        FROM users u
        WHERE NOT EXISTS (
            SELECT 1 FROM teachers t WHERE t.user_id = u.id
        ) AND u.role = 'teacher'
    """)

    # Create student profiles for users with active role = student.
    op.execute("""
        INSERT INTO students (user_id, grade_level, enrollment_date)
        SELECT u.id, NULL, NOW()
        FROM users u
        WHERE NOT EXISTS (
            SELECT 1 FROM students s WHERE s.user_id = u.id
        ) AND u.role = 'student'
    """)


def downgrade() -> None:
    """
    Downgrade: Remove profiles that were created by this migration.
    Note: This is a simplified downgrade and may not perfectly reverse the upgrade.
    """
    # We cannot safely remove profiles without knowing which ones were added
    # by this migration vs which existed before, so we skip the downgrade
    pass
