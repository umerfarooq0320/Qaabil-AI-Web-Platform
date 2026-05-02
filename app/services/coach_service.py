"""
Coach Service — handles voice analysis and coaching feedback.
"""

from datetime import datetime, timezone
from app.models.user import User
from app.agents.coach import analyze_voice, get_coaching_feedback
from app.agents.state import UserState
from app.db.mongodb import voice_sessions_collection, behavior_logs_collection


async def process_voice(user: User, transcript: str) -> dict:
    """Analyze a voice transcript and return feedback."""
    state: UserState = {
        "user_id": user.id,
        "profile": {
            "education": user.education_level or "college",
            "field": user.field_of_study or "general",
            "english_level": user.english_level or "medium",
        },
        "skill_vector": user.skill_vector or {},
    }
    analysis = await analyze_voice(state, transcript)
    try:
        await voice_sessions_collection().insert_one({
            "user_id": user.id, "transcript": transcript,
            "analysis": analysis, "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass
    return analysis


async def get_coaching(user: User, area: str = "general") -> dict:
    """Get personalized coaching feedback."""
    state: UserState = {
        "user_id": user.id,
        "profile": {
            "education": user.education_level or "college",
            "field": user.field_of_study or "general",
            "english_level": user.english_level or "medium",
        },
        "skill_vector": user.skill_vector or {},
        "trust_score": user.trust_score,
        "current_stage": user.current_stage,
    }
    return await get_coaching_feedback(state, area)
