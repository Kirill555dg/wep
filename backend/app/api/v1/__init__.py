"""
API v1 endpoints
"""

import fastapi

from app.api.v1 import attempts as attempts
from app.api.v1 import auth as auth
from app.api.v1 import catalog as catalog
from app.api.v1 import health as health
from app.api.v1 import stats as stats
from app.api.v1 import tags as tags
from app.api.v1 import tests as tests

api_router = fastapi.APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(tests.router, prefix="/tests", tags=["Tests"])
api_router.include_router(catalog.router, prefix="/catalog", tags=["Catalog"])
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])
api_router.include_router(attempts.router, prefix="/attempts", tags=["Attempts"])
api_router.include_router(stats.router, prefix="/stats", tags=["Stats"])
