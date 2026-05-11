"""
Theory materials models: Subject, Section, Subsection, TheoryMaterial, MaterialImage
"""

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app.core import datetime_extensions as dte
from app.db import session as db_session


class Subject(db_session.Base):
    """Subject/Course (Математика, Физика и т.д.)"""

    __tablename__ = "subjects"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String(255), unique=True, nullable=False, index=True)
    description = sa.Column(sa.Text, nullable=True)
    icon_url = sa.Column(sa.String(500), nullable=True)
    order_number = sa.Column(sa.Integer, default=0, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    # Relationships
    sections = orm.relationship("Section", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name='{self.name}')>"


class Section(db_session.Base):
    """Section within a subject (Раздел внутри предмета)"""

    __tablename__ = "sections"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    subject_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    order_number = sa.Column(sa.Integer, default=0, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    # Relationships
    subject = orm.relationship("Subject", back_populates="sections")
    subsections = orm.relationship("Subsection", back_populates="section", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Section(id={self.id}, name='{self.name}', subject_id={self.subject_id})>"


class Subsection(db_session.Base):
    """Subsection within a section (Подраздел внутри раздела)"""

    __tablename__ = "subsections"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    section_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    order_number = sa.Column(sa.Integer, default=0, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    # Relationships
    section = orm.relationship("Section", back_populates="subsections")
    theory_materials = orm.relationship(
        "TheoryMaterial", back_populates="subsection", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Subsection(id={self.id}, name='{self.name}', section_id={self.section_id})>"


class TheoryMaterial(db_session.Base):
    """Theory material/content"""

    __tablename__ = "theory_materials"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    subsection_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("subsections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = sa.Column(sa.String(255), nullable=False)
    content = sa.Column(sa.Text, nullable=False)  # основное содержание (может быть Markdown)
    order_number = sa.Column(sa.Integer, default=0, nullable=False)
    estimated_read_time = sa.Column(sa.Integer, nullable=True)  # примерное время чтения в минутах
    is_published = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=dte.utc_now,
        onupdate=dte.utc_now,
        nullable=False,
    )

    # Relationships
    subsection = orm.relationship("Subsection", back_populates="theory_materials")
    lesson_materials = orm.relationship(
        "LessonMaterial", back_populates="theory_material", cascade="all, delete-orphan"
    )
    images = orm.relationship("MaterialImage", back_populates="material", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<TheoryMaterial(id={self.id}, title='{self.title}')>"


class MaterialImage(db_session.Base):
    """Images attached to theory materials"""

    __tablename__ = "material_images"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    material_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("theory_materials.id", ondelete="CASCADE"),
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
    material = orm.relationship("TheoryMaterial", back_populates="images")
    file = orm.relationship("File")

    def __repr__(self) -> str:
        return f"<MaterialImage(id={self.id}, material_id={self.material_id})>"
