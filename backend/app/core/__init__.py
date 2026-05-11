"""
Core application components
"""

from app.core import config as core_config
from app.core import security as core_security

__all__ = [
    "settings",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
]

settings = core_config.settings
verify_password = core_security.verify_password
get_password_hash = core_security.get_password_hash
create_access_token = core_security.create_access_token
decode_access_token = core_security.decode_access_token
