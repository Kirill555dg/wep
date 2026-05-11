"""
Access control helpers for the services layer.

These helpers centralize common authorization checks and convert missing
profile/classroom references into ``ServiceError``. Routes are expected to
catch ``ServiceError`` and produce the appropriate HTTP response.
"""

from app.models import classes as classes_models
from app.models import users as user_models
from app.services import exceptions as service_exceptions


def require_teacher_profile(
    teacher: user_models.Teacher | None,
    *,
    detail: str,
) -> user_models.Teacher:
    """Return the teacher profile or raise ``ServiceError`` (``forbidden``)."""
    if not teacher:
        raise service_exceptions.ServiceError(detail, code="forbidden")
    return teacher


def require_classroom(
    classroom: classes_models.Classroom | None,
    *,
    detail: str = "Classroom not found",
) -> classes_models.Classroom:
    """Return the classroom or raise ``ServiceError`` (``not_found``)."""
    if not classroom:
        raise service_exceptions.ServiceError(detail, code="not_found")
    return classroom


def require_teacher_owns_classroom(
    *,
    teacher: user_models.Teacher,
    classroom: classes_models.Classroom,
    detail: str,
) -> None:
    """Raise ``ServiceError`` (``forbidden``) if the teacher does not own the classroom."""
    if classroom.teacher_id != teacher.id:
        raise service_exceptions.ServiceError(detail, code="forbidden")
