"""
User schemas — request/response models for auth and profile.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime


# ---- Auth ----

class UserSignup(BaseModel):
    email: EmailStr
    name: str
    password: str
    education_level: str | None = None
    field_of_study: str | None = None
    english_level: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str


# ---- Profile ----

class SkillVector(BaseModel):
    logical_reasoning: float = 0.0
    communication: float = 0.0
    confidence: float = 0.0
    learning_speed: str = "medium"
    hidden_strength: str = ""
    risk_area: str = ""


class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    education_level: str | None
    field_of_study: str | None
    english_level: str | None
    skill_vector: dict | None
    qabil_score: float
    trust_score: float
    current_stage: str
    intelligence_profile: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = None
    education_level: str | None = None
    field_of_study: str | None = None
    english_level: str | None = None
