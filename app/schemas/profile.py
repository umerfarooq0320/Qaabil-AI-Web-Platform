"""
Profile schemas — intelligence profile and learning path.
"""

from pydantic import BaseModel


class IntelligenceProfile(BaseModel):
    cognitive_ability: float = 0.0
    communication_skill: float = 0.0
    behavioral_traits: list[str] = []
    learning_velocity: str = "medium"
    consistency_score: float = 0.0
    career_fit_predictions: list[str] = []


class LearningPathDay(BaseModel):
    day: int
    tasks: list[str]
    focus_area: str
    estimated_time_min: int


class LearningPathResponse(BaseModel):
    user_id: str
    skill_gaps: list[str]
    learning_path: list[LearningPathDay]
    ai_reasoning: str
