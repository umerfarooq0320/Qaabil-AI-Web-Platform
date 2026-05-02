"""
Profile endpoints — user profile and learning path.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserProfile, UserUpdate
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["User Profile"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(user: User = Depends(get_current_user)):
    """Get current user's full profile."""
    return UserProfile.model_validate(user)


@router.patch("/me", response_model=UserProfile)
async def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile fields."""
    if data.name is not None:
        user.name = data.name
    if data.education_level is not None:
        user.education_level = data.education_level
    if data.field_of_study is not None:
        user.field_of_study = data.field_of_study
    if data.english_level is not None:
        user.english_level = data.english_level
    await db.flush()
    return UserProfile.model_validate(user)


@router.get("/learning-path")
async def get_learning_path(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated personalized learning path."""
    return await profile_service.get_learning_path(user, db)
