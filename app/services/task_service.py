"""
Task Service — generates tasks and evaluates submissions.
"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.task import Task
from app.models.skill import SkillSnapshot
from app.agents.task_agent import generate_task, evaluate_task_submission
from app.agents.verifier import verify_submission
from app.agents.state import UserState
from app.schemas.task import TaskResponse, TaskEvaluationResponse
from app.core.exceptions import QabilException
from app.db.mongodb import behavior_logs_collection


async def create_task(
    user: User,
    career_interest: str | None,
    db: AsyncSession,
) -> TaskResponse:
    """Generate a new AI task for the user."""
    # Get past tasks
    result = await db.execute(
        select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc()).limit(5)
    )
    past_tasks = [
        {"title": t.title, "type": t.task_type, "score": t.score}
        for t in result.scalars().all()
    ]

    state: UserState = {
        "user_id": user.id,
        "skill_vector": user.skill_vector or {},
    }

    task_data = await generate_task(state, career_interest or "", past_tasks)

    # Save to DB
    task = Task(
        user_id=user.id,
        title=task_data.get("title", "Untitled Task"),
        description=task_data.get("description", ""),
        difficulty=task_data.get("difficulty", "medium"),
        task_type=task_data.get("task_type", "general"),
        evaluation_rubric=task_data.get("evaluation_rubric"),
        status="pending",
    )
    db.add(task)
    await db.flush()

    return TaskResponse.model_validate(task)


async def submit_task(
    task_id: str,
    user: User,
    submission: str,
    db: AsyncSession,
) -> TaskEvaluationResponse:
    """Submit and evaluate a task."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise QabilException("Task not found", 404)
    if task.status == "evaluated":
        raise QabilException("Task already evaluated", 400)

    # Get past submissions for verification
    past_result = await db.execute(
        select(Task).where(
            Task.user_id == user.id,
            Task.status == "evaluated",
        ).order_by(Task.created_at.desc()).limit(3)
    )
    past_submissions = [t.submission for t in past_result.scalars().all() if t.submission]

    # Evaluate submission
    evaluation = await evaluate_task_submission(
        {"title": task.title, "description": task.description},
        submission,
        task.evaluation_rubric or {},
    )

    # Verify authenticity
    state: UserState = {"user_id": user.id, "trust_score": user.trust_score}
    verification = await verify_submission(state, submission, past_submissions)

    # Update task
    task.submission = submission
    task.submitted_at = datetime.now(timezone.utc)
    task.status = "evaluated"
    task.ai_evaluation = evaluation
    task.score = float(evaluation.get("total_score", 0))

    # Update user trust score
    new_trust = float(verification.get("trust_score", user.trust_score))
    user.trust_score = round((user.trust_score * 0.8) + (new_trust * 0.2), 3)

    await db.flush()

    # Log
    try:
        await behavior_logs_collection().insert_one({
            "user_id": user.id,
            "event_type": "task_submitted",
            "task_id": task_id,
            "score": task.score,
            "trust_update": user.trust_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass

    return TaskEvaluationResponse(
        task_id=task.id,
        score=task.score,
        evaluation=evaluation,
        trust_score_update=user.trust_score,
        feedback=evaluation.get("feedback", ""),
    )


async def get_task_history(user: User, db: AsyncSession) -> list[TaskResponse]:
    """Get all tasks for a user."""
    result = await db.execute(
        select(Task).where(Task.user_id == user.id).order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    return [TaskResponse.model_validate(t) for t in tasks]
