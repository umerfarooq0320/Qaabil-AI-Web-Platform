"""
Task endpoints — generate tasks, submit work, view history.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.task import (
    TaskGenerateRequest, TaskResponse,
    TaskSubmitRequest, TaskEvaluationResponse,
)
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks (Proof of Work)"])


@router.post("/generate", response_model=TaskResponse)
async def generate_task(
    data: TaskGenerateRequest = TaskGenerateRequest(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new AI task based on user's skill level."""
    return await task_service.create_task(user, data.career_interest, db)


@router.post("/{task_id}/submit", response_model=TaskEvaluationResponse)
async def submit_task(
    task_id: str,
    data: TaskSubmitRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a task and get AI evaluation."""
    return await task_service.submit_task(task_id, user, data.submission, db)


@router.get("/history", response_model=list[TaskResponse])
async def task_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all tasks for the current user."""
    return await task_service.get_task_history(user, db)
