"""
Career passport model — AI-generated career profile.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.postgres import Base


class CareerPassport(Base):
    __tablename__ = "career_passports"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), unique=True, nullable=False
    )

    qabil_score: Mapped[float] = mapped_column(Float, default=0.0)
    skill_graph: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    communication_rating: Mapped[str | None] = mapped_column(String(10), nullable=True)
    work_proofs: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    trust_score: Mapped[float] = mapped_column(Float, default=1.0)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Job matching data
    matched_jobs: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="career_passport")
