"""
Pagination defaults and limits.

Kept in core to avoid hardcoding pagination numbers across the codebase.
"""

from app.core import config as core_config


DEFAULT_SKIP: int = core_config.settings.PAGINATION_DEFAULT_SKIP
DEFAULT_LIMIT: int = core_config.settings.PAGINATION_DEFAULT_LIMIT
MAX_LIMIT: int = core_config.settings.PAGINATION_MAX_LIMIT

