"""
User model — the core entity in QABIL.
Stores profile, skill vector, scores, and current stage.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.postgres import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile info
    education_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    field_of_study: Mapped[str | None] = mapped_column(String(255), nullable=True)
    english_level: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # AI-generated fields
    skill_vector: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    qabil_score: Mapped[float] = mapped_column(Float, default=0.0)
    trust_score: Mapped[float] = mapped_column(Float, default=1.0)
    current_stage: Mapped[str] = mapped_column(String(50), default="onboarding")

    # Intelligence profile (built by Profiler Agent)
    intelligence_profile: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    quiz_sessions = relationship("QuizSession", back_populates="user", lazy="selectin")
    tasks = relationship("Task", back_populates="user", lazy="selectin")
    career_passport = relationship("CareerPassport", back_populates="user", uselist=False, lazy="selectin")

    def __repr__(self):
        return f"<User {self.email}>"
