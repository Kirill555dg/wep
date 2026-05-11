"""
API v1 endpoints
"""

import fastapi

from app.api.v1 import auth as auth
from app.api.v1 import classrooms as classrooms
from app.api.v1 import health as health
from app.api.v1 import homework as homework
from app.api.v1 import lessons as lessons
from app.api.v1 import problems as problems
from app.api.v1 import statistics as statistics
from app.api.v1 import theory as theory
from app.api.v1 import testing as testing

api_router = fastapi.APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(classrooms.router, prefix="/classrooms", tags=["Classrooms"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
api_router.include_router(homework.router, prefix="/homework", tags=["Homework"])
api_router.include_router(problems.router, prefix="/problems", tags=["Problems"])
api_router.include_router(testing.router, prefix="/testing", tags=["Testing"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
api_router.include_router(theory.router, prefix="/theory", tags=["Theory"])
