"""
Business logic services
"""

from app.services import auth as auth_service

AuthService = auth_service.AuthService

__all__ = ["AuthService"]
