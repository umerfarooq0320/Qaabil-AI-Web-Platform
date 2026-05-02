"""
Profile Service — manages intelligence profiles and learning paths.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.agents.profiler import generate_learning_path
from app.agents.state import UserState


async def get_learning_path(user: User, db: AsyncSession) -> dict:
    """
    Generate a personalized learning path for the user.
    """
    state: UserState = {
        "user_id": user.id,
        "profile": {
            "education": user.education_level or "college",
            "field": user.field_of_study or "general",
            "english_level": user.english_level or "medium",
        },
        "skill_vector": user.skill_vector or {},
        "intelligence_profile": user.intelligence_profile or {},
        "progress_history": [],
    }

    path = await generate_learning_path(state)

    return {
        "user_id": user.id,
        **path,
    }
