"""
API v1 endpoints
"""

import fastapi

from app.api.v1 import auth as auth
from app.api.v1 import health as health

api_router = fastapi.APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
