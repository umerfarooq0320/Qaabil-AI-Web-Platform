"""
Coach endpoints — voice analysis and coaching.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user
from app.models.user import User
from app.services import coach_service

router = APIRouter(prefix="/coach", tags=["Coach (Rahnuma)"])


class VoiceRequest(BaseModel):
    transcript: str


class CoachRequest(BaseModel):
    area: str = "general"


@router.post("/voice")
async def analyze_voice(
    data: VoiceRequest,
    user: User = Depends(get_current_user),
):
    """Analyze voice transcript for communication skills."""
    return await coach_service.process_voice(user, data.transcript)


@router.post("/feedback")
async def get_feedback(
    data: CoachRequest = CoachRequest(),
    user: User = Depends(get_current_user),
):
    """Get personalized coaching feedback."""
    return await coach_service.get_coaching(user, data.area)
