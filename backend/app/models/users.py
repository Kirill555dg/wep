import sqlalchemy as sa
import sqlalchemy.orm as sqla_orm

from app.core import datetime_extensions as dte
from app.db import session as db_session


class User(db_session.Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    username = sa.Column(sa.String(100), unique=True, nullable=False, index=True)
    email = sa.Column(sa.String(255), unique=True, nullable=False, index=True)
    first_name = sa.Column(sa.String(100), nullable=False)
    last_name = sa.Column(sa.String(100), nullable=False)
    middle_name = sa.Column(sa.String(100), nullable=True)
    full_name = sa.Column(sa.String(255), nullable=False)
    role = sa.Column(sa.String(20), nullable=False, default="student")
    avatar_url = sa.Column(sa.String(500), nullable=True)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    updated_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, onupdate=dte.utc_now, nullable=False)

    login_data = sqla_orm.relationship("LoginData", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher = sqla_orm.relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student = sqla_orm.relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class LoginData(db_session.Base):
    __tablename__ = "login_data"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    hashed_password = sa.Column(sa.String(255), nullable=False)
    last_login = sa.Column(sa.DateTime(timezone=True), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    user = sqla_orm.relationship("User", back_populates="login_data")

    def __repr__(self) -> str:
        return f"<LoginData(user_id={self.user_id})>"


class Teacher(db_session.Base):
    __tablename__ = "teachers"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio = sa.Column(sa.Text, nullable=True)
    subject_specialization = sa.Column(sa.String(255), nullable=True)
    years_of_experience = sa.Column(sa.Integer, default=0)
    rating = sa.Column(sa.Integer, default=0)

    user = sqla_orm.relationship("User", back_populates="teacher")

    def __repr__(self) -> str:
        return f"<Teacher(id={self.id}, user_id={self.user_id})>"


class Student(db_session.Base):
    __tablename__ = "students"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    grade_level = sa.Column(sa.Integer, nullable=True)
    student_id_number = sa.Column(sa.String(50), unique=True, nullable=True)
    enrollment_date = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    user = sqla_orm.relationship("User", back_populates="student")

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, user_id={self.user_id}, grade_level={self.grade_level})>"
