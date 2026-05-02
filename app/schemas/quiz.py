"""
Quiz schemas — request/response models for adaptive quiz.
"""

from pydantic import BaseModel
from datetime import datetime


class QuizStartRequest(BaseModel):
    """Optional overrides when starting a quiz."""
    num_questions: int = 5  # How many questions in this session


class QuizStartResponse(BaseModel):
    session_id: str
    question_number: int
    difficulty: str
    question: str
    options: list[str]


class QuizAnswerRequest(BaseModel):
    user_answer: str
    response_time_sec: float  # Frontend should track this


class QuizAnswerResponse(BaseModel):
    is_correct: bool
    score: float
    feedback: str
    # Next question (null if quiz is complete)
    next_question: dict | None = None
    quiz_complete: bool = False


class QuizReportResponse(BaseModel):
    session_id: str
    total_questions: int
    avg_score: float
    avg_response_time: float
    scores: list[float]
    final_report: dict | None
    skill_vector: dict | None
    qabil_score: float
