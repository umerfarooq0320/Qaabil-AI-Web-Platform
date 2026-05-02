"""
Quiz endpoints — start quiz, submit answers, get report.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.quiz import (
    QuizStartRequest, QuizStartResponse,
    QuizAnswerRequest, QuizAnswerResponse,
    QuizReportResponse,
)
from app.services import quiz_service

router = APIRouter(prefix="/quiz", tags=["Adaptive Quiz"])


@router.post("/start", response_model=QuizStartResponse)
async def start_quiz(
    data: QuizStartRequest = QuizStartRequest(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new adaptive quiz session."""
    return await quiz_service.start_quiz(user, data.num_questions, db)


@router.post("/{session_id}/answer", response_model=QuizAnswerResponse)
async def answer_question(
    session_id: str,
    data: QuizAnswerRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit an answer and get evaluation + next question."""
    return await quiz_service.answer_question(session_id, user, data, db)


@router.get("/{session_id}/report", response_model=QuizReportResponse)
async def get_report(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the final report for a completed quiz."""
    return await quiz_service.get_quiz_report(session_id, user, db)
