"""
Security utilities for password hashing and JWT
"""

import logging
import typing as tp

import datetime as dt

import argon2
import argon2.exceptions as argon2_exceptions
import jose.exceptions as jose_exceptions
import jose.jwt as jose_jwt

from app.core import config as core_config
from app.core import datetime_extensions as dte

# Note: logger name is stable for config filters/formatters.
logger = logging.getLogger("app.security")

# Initialize Argon2 password hasher with recommended parameters
# Argon2id is the recommended variant (hybrid of Argon2i and Argon2d)
ph = argon2.PasswordHasher(
    time_cost=2,  # Number of iterations
    memory_cost=65536,  # Memory usage in KiB (64 MB)
    parallelism=1,  # Number of parallel threads
    hash_len=32,  # Length of the hash in bytes
    salt_len=16,  # Length of random salt in bytes
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against Argon2 hash

    Args:
        plain_password: Plain text password
        hashed_password: Argon2 hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    try:
        ph.verify(hashed_password, plain_password)

        # Check if hash needs rehashing (parameters changed)
        if ph.check_needs_rehash(hashed_password):
            logger.info("password_hash_needs_update")

        return True
    except argon2_exceptions.VerifyMismatchError:
        return False
    except Exception as e:
        logger.exception("password_verification_error", extra={"error": str(e)})
        return False


def get_password_hash(password: str) -> str:
    """
    Hash password using Argon2id

    Args:
        password: Plain text password

    Returns:
        Argon2 hashed password
    """
    if not isinstance(password, str):
        raise ValueError(f"Password must be a string, got {type(password)}")

    if not password:
        raise ValueError("Password cannot be empty")

    return ph.hash(password)


def create_access_token(
    data: dict[str, tp.Any],
    expires_delta: dt.timedelta | None = None,
) -> str:
    """
    Create JWT access token

    Args:
        data: Data to encode in token
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = dte.utc_now() + expires_delta
    else:
        expire = dte.utc_now() + dt.timedelta(
            minutes=core_config.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jose_jwt.encode(
        to_encode,
        core_config.settings.SECRET_KEY,
        algorithm=core_config.settings.ALGORITHM,
    )
    return tp.cast(str, encoded_jwt)


def decode_access_token(token: str) -> dict[str, tp.Any] | None:
    """
    Decode JWT access token

    Args:
        token: JWT token string

    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jose_jwt.decode(
            token,
            core_config.settings.SECRET_KEY,
            algorithms=[core_config.settings.ALGORITHM],
        )
        return tp.cast(dict[str, tp.Any], payload)
    except jose_exceptions.JWTError:
        return None
