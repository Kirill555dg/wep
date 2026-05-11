"""create all LMS tables

Revision ID: 765d7038a0e6
Revises:
Create Date: 2025-12-07 22:08:26.052825

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "765d7038a0e6"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Extensions are used for future features (ids/search), safe to keep idempotent.
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    op.create_table(
        "files",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_files_file_hash"), "files", ["file_hash"], unique=False)
    op.create_index(op.f("ix_files_id"), "files", ["id"], unique=False)

    op.create_table(
        "problems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("problem_type", sa.String(length=50), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("hints", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_problems_id"), "problems", ["id"], unique=False)

    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon_url", sa.String(length=500), nullable=True),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subjects_id"), "subjects", ["id"], unique=False)
    op.create_index(op.f("ix_subjects_name"), "subjects", ["name"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("middle_name", sa.String(length=100), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "login_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_login_data_id"), "login_data", ["id"], unique=False)

    op.create_table(
        "problem_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=True),
        sa.Column("caption", sa.String(length=255), nullable=True),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_problem_images_id"), "problem_images", ["id"], unique=False)
    op.create_index(op.f("ix_problem_images_problem_id"), "problem_images", ["problem_id"], unique=False)

    op.create_table(
        "sections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sections_id"), "sections", ["id"], unique=False)
    op.create_index(op.f("ix_sections_subject_id"), "sections", ["subject_id"], unique=False)

    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("grade_level", sa.Integer(), nullable=True),
        sa.Column("student_id_number", sa.String(length=50), nullable=True),
        sa.Column("enrollment_date", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id_number"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_students_id"), "students", ["id"], unique=False)

    op.create_table(
        "teachers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("subject_specialization", sa.String(length=255), nullable=True),
        sa.Column("years_of_experience", sa.Integer(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_teachers_id"), "teachers", ["id"], unique=False)

    op.create_table(
        "classrooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("subject", sa.String(length=100), nullable=False),
        sa.Column("grade_level", sa.Integer(), nullable=True),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("max_students", sa.Integer(), nullable=True),
        sa.Column("invite_code", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invite_code"),
    )
    op.create_index(op.f("ix_classrooms_id"), "classrooms", ["id"], unique=False)

    op.create_table(
        "subsections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("section_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["section_id"], ["sections.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subsections_id"), "subsections", ["id"], unique=False)
    op.create_index(op.f("ix_subsections_section_id"), "subsections", ["section_id"], unique=False)

    op.create_table(
        "chats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("classroom_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["classroom_id"], ["classrooms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("classroom_id"),
    )
    op.create_index(op.f("ix_chats_id"), "chats", ["id"], unique=False)

    op.create_table(
        "invites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("classroom_id", sa.Integer(), nullable=False),
        sa.Column("invite_code", sa.String(length=100), nullable=False),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column("uses_count", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "ACCEPTED", "REJECTED", "EXPIRED", name="invitestatus"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["classroom_id"], ["classrooms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invites_id"), "invites", ["id"], unique=False)
    op.create_index(op.f("ix_invites_invite_code"), "invites", ["invite_code"], unique=True)

    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("classroom_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order_number", sa.Integer(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["classroom_id"], ["classrooms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lessons_classroom_id"), "lessons", ["classroom_id"], unique=False)
    op.create_index(op.f("ix_lessons_id"), "lessons", ["id"], unique=False)

    op.create_table(
        "student_classrooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("classroom_id", sa.Integer(), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["classroom_id"], ["classrooms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_classrooms_id"), "student_classrooms", ["id"], unique=False)

    op.create_table(
        "theory_materials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subsection_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("estimated_read_time", sa.Integer(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["subsection_id"], ["subsections.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_theory_materials_id"), "theory_materials", ["id"], unique=False)
    op.create_index(
        op.f("ix_theory_materials_subsection_id"), "theory_materials", ["subsection_id"], unique=False
    )

    op.create_table(
        "homeworks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("max_score", sa.Float(), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_homeworks_id"), "homeworks", ["id"], unique=False)
    op.create_index(op.f("ix_homeworks_lesson_id"), "homeworks", ["lesson_id"], unique=False)

    op.create_table(
        "lesson_materials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("theory_material_id", sa.Integer(), nullable=False),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["theory_material_id"], ["theory_materials.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lesson_materials_id"), "lesson_materials", ["id"], unique=False)

    op.create_table(
        "material_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=True),
        sa.Column("caption", sa.String(length=255), nullable=True),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["material_id"], ["theory_materials.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_material_images_id"), "material_images", ["id"], unique=False)
    op.create_index(op.f("ix_material_images_material_id"), "material_images", ["material_id"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_edited", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_chat_id"), "messages", ["chat_id"], unique=False)
    op.create_index(op.f("ix_messages_created_at"), "messages", ["created_at"], unique=False)
    op.create_index(op.f("ix_messages_id"), "messages", ["id"], unique=False)

    op.create_table(
        "homework_problems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("homework_id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("points", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["homework_id"], ["homeworks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_homework_problems_id"), "homework_problems", ["id"], unique=False)

    op.create_table(
        "statistics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("homework_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("NOT_STARTED", "IN_PROGRESS", "SUBMITTED", "GRADED", name="homeworkstatus"),
            nullable=False,
        ),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("max_score", sa.Float(), nullable=False),
        sa.Column("attempts_count", sa.Integer(), nullable=False),
        sa.Column("time_spent_minutes", sa.Integer(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("graded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["homework_id"], ["homeworks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_statistics_homework_id"), "statistics", ["homework_id"], unique=False)
    op.create_index(op.f("ix_statistics_id"), "statistics", ["id"], unique=False)
    op.create_index(op.f("ix_statistics_student_id"), "statistics", ["student_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_statistics_student_id"), table_name="statistics")
    op.drop_index(op.f("ix_statistics_id"), table_name="statistics")
    op.drop_index(op.f("ix_statistics_homework_id"), table_name="statistics")
    op.drop_table("statistics")
    op.drop_index(op.f("ix_homework_problems_id"), table_name="homework_problems")
    op.drop_table("homework_problems")
    op.drop_index(op.f("ix_messages_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_created_at"), table_name="messages")
    op.drop_index(op.f("ix_messages_chat_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_material_images_material_id"), table_name="material_images")
    op.drop_index(op.f("ix_material_images_id"), table_name="material_images")
    op.drop_table("material_images")
    op.drop_index(op.f("ix_lesson_materials_id"), table_name="lesson_materials")
    op.drop_table("lesson_materials")
    op.drop_index(op.f("ix_homeworks_lesson_id"), table_name="homeworks")
    op.drop_index(op.f("ix_homeworks_id"), table_name="homeworks")
    op.drop_table("homeworks")
    op.drop_index(op.f("ix_theory_materials_subsection_id"), table_name="theory_materials")
    op.drop_index(op.f("ix_theory_materials_id"), table_name="theory_materials")
    op.drop_table("theory_materials")
    op.drop_index(op.f("ix_student_classrooms_id"), table_name="student_classrooms")
    op.drop_table("student_classrooms")
    op.drop_index(op.f("ix_lessons_id"), table_name="lessons")
    op.drop_index(op.f("ix_lessons_classroom_id"), table_name="lessons")
    op.drop_table("lessons")
    op.drop_index(op.f("ix_invites_invite_code"), table_name="invites")
    op.drop_index(op.f("ix_invites_id"), table_name="invites")
    op.drop_table("invites")
    op.drop_index(op.f("ix_chats_id"), table_name="chats")
    op.drop_table("chats")
    op.drop_index(op.f("ix_subsections_section_id"), table_name="subsections")
    op.drop_index(op.f("ix_subsections_id"), table_name="subsections")
    op.drop_table("subsections")
    op.drop_index(op.f("ix_classrooms_id"), table_name="classrooms")
    op.drop_table("classrooms")
    op.drop_index(op.f("ix_teachers_id"), table_name="teachers")
    op.drop_table("teachers")
    op.drop_index(op.f("ix_students_id"), table_name="students")
    op.drop_table("students")
    op.drop_index(op.f("ix_sections_subject_id"), table_name="sections")
    op.drop_index(op.f("ix_sections_id"), table_name="sections")
    op.drop_table("sections")
    op.drop_index(op.f("ix_problem_images_problem_id"), table_name="problem_images")
    op.drop_index(op.f("ix_problem_images_id"), table_name="problem_images")
    op.drop_table("problem_images")
    op.drop_index(op.f("ix_login_data_id"), table_name="login_data")
    op.drop_table("login_data")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_subjects_name"), table_name="subjects")
    op.drop_index(op.f("ix_subjects_id"), table_name="subjects")
    op.drop_table("subjects")
    op.drop_index(op.f("ix_problems_id"), table_name="problems")
    op.drop_table("problems")
    op.drop_index(op.f("ix_files_id"), table_name="files")
    op.drop_index(op.f("ix_files_file_hash"), table_name="files")
    op.drop_table("files")

    # Clean up enum types (PostgreSQL doesn't drop them automatically).
    op.execute("DROP TYPE IF EXISTS invitestatus")
    op.execute("DROP TYPE IF EXISTS homeworkstatus")
