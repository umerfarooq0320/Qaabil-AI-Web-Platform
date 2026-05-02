"""
Career endpoints — passport and job matching.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services import career_service

router = APIRouter(prefix="/career", tags=["Career Passport"])


@router.get("/passport")
async def get_passport(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get or generate career passport."""
    return await career_service.get_or_build_passport(user, db)


@router.get("/jobs")
async def get_jobs(user: User = Depends(get_current_user)):
    """Get AI-matched job recommendations."""
    return await career_service.get_job_matches(user)
