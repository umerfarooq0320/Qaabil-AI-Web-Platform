"""
Task schemas — proof-of-work task generation and submission.
"""

from pydantic import BaseModel
from datetime import datetime


class TaskGenerateRequest(BaseModel):
    career_interest: str | None = None
    preferred_type: str | None = None  # writing / logic / scenario


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    task_type: str
    evaluation_rubric: dict | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskSubmitRequest(BaseModel):
    submission: str


class TaskEvaluationResponse(BaseModel):
    task_id: str
    score: float
    evaluation: dict
    trust_score_update: float
    feedback: str
