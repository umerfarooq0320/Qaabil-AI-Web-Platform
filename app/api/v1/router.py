"""
V1 API Router — aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.quiz import router as quiz_router
from app.api.v1.profile import router as profile_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.coach import router as coach_router
from app.api.v1.career import router as career_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(quiz_router)
router.include_router(profile_router)
router.include_router(tasks_router)
router.include_router(coach_router)
router.include_router(career_router)
