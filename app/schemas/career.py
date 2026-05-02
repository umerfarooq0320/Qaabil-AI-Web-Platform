"""
Career schemas — passport and job matching.
"""

from pydantic import BaseModel
from datetime import datetime


class CareerPassportResponse(BaseModel):
    qabil_score: float
    skill_graph: dict | None
    communication_rating: str | None
    work_proofs: list | None
    trust_score: float
    ai_summary: str | None
    generated_at: datetime

    model_config = {"from_attributes": True}


class JobMatch(BaseModel):
    title: str
    company: str
    match_score: float
    skill_fit: float
    communication_fit: float
    why_matched: str


class JobMatchResponse(BaseModel):
    user_id: str
    matches: list[JobMatch]
    auto_resume: str | None = None
    auto_cover_letter: str | None = None
