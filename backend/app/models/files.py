"""
File storage model
"""

import sqlalchemy as sa

from app.core import datetime_extensions as dte
from app.db import session as db_session


class File(db_session.Base):
    """File storage model for uploaded files"""

    __tablename__ = "files"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    filename = sa.Column(sa.String(255), nullable=False)
    original_filename = sa.Column(sa.String(255), nullable=False)
    file_path = sa.Column(sa.String(500), nullable=False)  # путь к файлу на диске/S3
    file_size = sa.Column(sa.BigInteger, nullable=False)  # размер в байтах
    mime_type = sa.Column(sa.String(100), nullable=False)
    file_hash = sa.Column(sa.String(64), nullable=True, index=True)  # SHA-256 hash для дедупликации
    is_public = sa.Column(sa.Boolean, default=False, nullable=False)
    uploaded_by = sa.Column(sa.Integer, nullable=True)  # user_id who uploaded
    created_at = sa.Column(sa.DateTime(timezone=True), default=dte.utc_now, nullable=False)

    def __repr__(self) -> str:
        return f"<File(id={self.id}, filename='{self.filename}', size={self.file_size})>"
