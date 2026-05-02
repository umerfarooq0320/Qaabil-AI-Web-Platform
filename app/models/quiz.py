"""
Quiz models — sessions and individual answers.
Tracks adaptive quiz flow with timing and difficulty.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.postgres import Base


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(String(20), default="active")  # active / completed / abandoned
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    current_difficulty: Mapped[str] = mapped_column(String(20), default="medium")
    avg_score: Mapped[float] = mapped_column(Float, default=0.0)
    avg_response_time: Mapped[float] = mapped_column(Float, default=0.0)

    # AI-generated final report
    final_report: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # The current question waiting for an answer (stored as JSON)
    current_question: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="quiz_sessions")
    answers = relationship("QuizAnswer", back_populates="session", lazy="selectin")

    def __repr__(self):
        return f"<QuizSession {self.id} status={self.status}>"


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("quiz_sessions.id"), nullable=False, index=True
    )

    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)

    # Full question data from AI
    question_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(500), nullable=False)

    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    response_time_sec: Mapped[float] = mapped_column(Float, default=0.0)

    # AI feedback for this answer
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    session = relationship("QuizSession", back_populates="answers")
