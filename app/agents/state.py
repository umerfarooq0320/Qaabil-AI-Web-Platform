"""
UserState — the shared state object that flows through all agents.
This is the TypedDict used by LangGraph for state management.
"""

from typing import TypedDict, Annotated
from operator import add


class SkillVector(TypedDict, total=False):
    logical_reasoning: float
    communication: float
    confidence: float
    learning_speed: str
    hidden_strength: str
    risk_area: str


class UserProfile(TypedDict, total=False):
    education: str
    field: str
    english_level: str


class QuizContext(TypedDict, total=False):
    session_id: str
    current_difficulty: str
    questions_asked: int
    max_questions: int
    scores: list[float]
    response_times: list[float]
    current_question: dict
    is_complete: bool


class TaskContext(TypedDict, total=False):
    task_id: str
    submission: str
    evaluation: dict


class UserState(TypedDict, total=False):
    """
    The central state object for a user.
    Passed between agents via LangGraph.
    """
    # Identity
    user_id: str

    # Profile
    profile: UserProfile

    # Skills (evolving)
    skill_vector: SkillVector

    # Behavior tracking
    behavior_log: list[dict]

    # Trust
    trust_score: float

    # Progress
    progress_history: list[dict]

    # Current stage: onboarding / active / advanced
    current_stage: str

    # Quiz state (when running quiz)
    quiz_context: QuizContext

    # Task state (when running tasks)
    task_context: TaskContext

    # Which agent ran last
    last_agent: str

    # What action triggered this flow
    trigger: str

    # Errors (if any)
    errors: list[str]

    # Messages / feedback to return to user
    messages: list[str]
