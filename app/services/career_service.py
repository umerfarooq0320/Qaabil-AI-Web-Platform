"""
Career Service — career passport and job matching.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.task import Task
from app.models.career import CareerPassport
from app.agents.career import build_career_passport, match_jobs
from app.agents.state import UserState


async def get_or_build_passport(user: User, db: AsyncSession) -> dict:
    """Get existing passport or build a new one."""
    result = await db.execute(
        select(CareerPassport).where(CareerPassport.user_id == user.id)
    )
    existing = result.scalar_one_or_none()

    # Get work proofs
    tasks_result = await db.execute(
        select(Task).where(Task.user_id == user.id, Task.status == "evaluated")
    )
    work_proofs = [
        {"title": t.title, "score": t.score, "type": t.task_type}
        for t in tasks_result.scalars().all()
    ]

    state: UserState = {
        "user_id": user.id,
        "profile": {
            "education": user.education_level or "",
            "field": user.field_of_study or "",
            "english_level": user.english_level or "",
        },
        "skill_vector": user.skill_vector or {},
        "intelligence_profile": user.intelligence_profile or {},
        "trust_score": user.trust_score,
    }

    passport_data = await build_career_passport(state, work_proofs)

    if existing:
        existing.qabil_score = user.qabil_score
        existing.skill_graph = user.skill_vector
        existing.trust_score = user.trust_score
        existing.ai_summary = passport_data.get("ai_summary", "")
        existing.work_proofs = work_proofs
    else:
        existing = CareerPassport(
            user_id=user.id,
            qabil_score=user.qabil_score,
            skill_graph=user.skill_vector,
            communication_rating=passport_data.get("communication_rating", ""),
            work_proofs=work_proofs,
            trust_score=user.trust_score,
            ai_summary=passport_data.get("ai_summary", ""),
        )
        db.add(existing)

    await db.flush()
    return passport_data


async def get_job_matches(user: User) -> dict:
    """Match user to suitable jobs."""
    state: UserState = {
        "user_id": user.id,
        "skill_vector": user.skill_vector or {},
        "trust_score": user.trust_score,
        "current_stage": user.current_stage,
    }
    return await match_jobs(state)
