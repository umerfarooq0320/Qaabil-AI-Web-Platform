"""
Skill snapshots — tracks skill vector evolution over time.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.postgres import Base


class SkillSnapshot(Base):
    __tablename__ = "skill_snapshots"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True
    )

    # What triggered this snapshot
    trigger: Mapped[str] = mapped_column(String(50), nullable=False)  # quiz / task / voice / daily

    # The full skill vector at this point in time
    skill_vector: Mapped[dict] = mapped_column(JSON, nullable=False)
    qabil_score: Mapped[float] = mapped_column(Float, default=0.0)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
