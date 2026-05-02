"""
Quiz Service — orchestrates the adaptive quiz flow.

Connects the API layer to the Assessor Agent.
Manages quiz sessions and answers in PostgreSQL.
"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.quiz import QuizSession, QuizAnswer
from app.models.skill import SkillSnapshot
from app.agents.assessor import (
    generate_question,
    evaluate_answer,
    generate_final_report,
    get_initial_difficulty,
)
from app.agents.profiler import build_intelligence_profile
from app.agents.state import UserState
from app.schemas.quiz import (
    QuizStartResponse,
    QuizAnswerRequest,
    QuizAnswerResponse,
    QuizReportResponse,
)
from app.core.exceptions import QuizError
from app.db.mongodb import behavior_logs_collection


async def start_quiz(user: User, num_questions: int, db: AsyncSession) -> QuizStartResponse:
    """
    Start a new adaptive quiz session.

    1. Creates a QuizSession in DB
    2. Builds initial UserState
    3. Runs Assessor Agent to generate first question
    """
    # Determine initial difficulty from education level
    difficulty = get_initial_difficulty(user.education_level or "college")

    # Create session in DB
    session = QuizSession(
        user_id=user.id,
        status="active",
        current_difficulty=difficulty,
    )
    db.add(session)
    await db.flush()

    # Build agent state
    state: UserState = {
        "user_id": user.id,
        "profile": {
            "education": user.education_level or "college",
            "field": user.field_of_study or "general",
            "english_level": user.english_level or "medium",
        },
        "skill_vector": user.skill_vector or {},
        "quiz_context": {
            "session_id": session.id,
            "current_difficulty": difficulty,
            "questions_asked": 0,
            "max_questions": num_questions,
            "scores": [],
            "response_times": [],
            "is_complete": False,
        },
        "trigger": "new_user",
        "errors": [],
        "messages": [],
    }

    # Generate first question
    state = await generate_question(state)

    if state.get("errors"):
        raise QuizError(f"Failed to start quiz: {state['errors']}")

    question = state["quiz_context"]["current_question"]

    # Store current question in session
    session.current_question = question
    await db.flush()

    # Log behavior
    try:
        await behavior_logs_collection().insert_one({
            "user_id": user.id,
            "event_type": "quiz_started",
            "session_id": session.id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass  # Non-critical

    return QuizStartResponse(
        session_id=session.id,
        question_number=1,
        difficulty=difficulty,
        question=question.get("question", ""),
        options=question.get("options", []),
    )


async def answer_question(
    session_id: str,
    user: User,
    data: QuizAnswerRequest,
    db: AsyncSession,
) -> QuizAnswerResponse:
    """
    Submit an answer, get AI evaluation and next question.

    1. Evaluates the answer via Assessor Agent
    2. Saves the answer to DB
    3. Adjusts difficulty
    4. Generates next question (or completes quiz)
    """
    # Get session
    result = await db.execute(
        select(QuizSession).where(
            QuizSession.id == session_id,
            QuizSession.user_id == user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise QuizError("Quiz session not found")
    if session.status != "active":
        raise QuizError("Quiz session is not active")

    current_question = session.current_question
    if not current_question:
        raise QuizError("No current question in session")

    # Count existing answers
    ans_result = await db.execute(
        select(QuizAnswer).where(QuizAnswer.session_id == session_id)
    )
    existing_answers = ans_result.scalars().all()
    question_number = len(existing_answers) + 1

    # Collect scores and times from existing answers
    existing_scores = [a.score for a in existing_answers]
    existing_times = [a.response_time_sec for a in existing_answers]

    # Build state for agent
    state: UserState = {
        "user_id": user.id,
        "profile": {
            "education": user.education_level or "college",
            "field": user.field_of_study or "general",
            "english_level": user.english_level or "medium",
        },
        "skill_vector": user.skill_vector or {},
        "quiz_context": {
            "session_id": session_id,
            "current_difficulty": session.current_difficulty,
            "questions_asked": question_number - 1,
            "max_questions": 5,  # Default
            "scores": existing_scores,
            "response_times": existing_times,
            "current_question": current_question,
            "is_complete": False,
        },
        "trigger": "quiz_answer",
        "errors": [],
        "messages": [],
    }

    # Evaluate answer
    state = await evaluate_answer(state, data.user_answer, data.response_time_sec)

    if state.get("errors"):
        raise QuizError(f"Evaluation failed: {state['errors']}")

    evaluation = state["quiz_context"].get("last_evaluation", {})

    # Save answer to DB
    answer = QuizAnswer(
        session_id=session_id,
        question_number=question_number,
        difficulty=session.current_difficulty,
        question_data=current_question,
        user_answer=data.user_answer,
        correct_answer=current_question.get("correct_answer", ""),
        is_correct=bool(evaluation.get("is_correct", False)),
        score=float(evaluation.get("score", 0)),
        response_time_sec=data.response_time_sec,
        feedback=evaluation.get("feedback", ""),
    )
    db.add(answer)

    # Update session difficulty
    session.current_difficulty = state["quiz_context"]["current_difficulty"]
    session.total_questions = question_number

    # Update averages
    all_scores = existing_scores + [float(evaluation.get("score", 0))]
    all_times = existing_times + [data.response_time_sec]
    session.avg_score = sum(all_scores) / len(all_scores)
    session.avg_response_time = sum(all_times) / len(all_times)

    # Check if quiz is complete
    quiz_complete = state["quiz_context"].get("is_complete", False)

    next_question_data = None

    if quiz_complete:
        # Generate final report
        state = await generate_final_report(state)

        # Build intelligence profile
        state = await build_intelligence_profile(state)

        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        session.final_report = state["quiz_context"].get("final_report")
        session.current_question = None

        # Update user's skill vector and score
        if state.get("skill_vector"):
            user.skill_vector = state["skill_vector"]
            # Calculate Qabil score as weighted average of skills
            sv = state["skill_vector"]
            numeric = [v for v in sv.values() if isinstance(v, (int, float))]
            if numeric:
                user.qabil_score = round(sum(numeric) / len(numeric) * 100, 1)

        if state.get("intelligence_profile"):
            user.intelligence_profile = state.get("intelligence_profile")

        user.current_stage = "active"

        # Save skill snapshot
        if state.get("skill_vector"):
            snapshot = SkillSnapshot(
                user_id=user.id,
                trigger="quiz",
                skill_vector=state["skill_vector"],
                qabil_score=user.qabil_score,
            )
            db.add(snapshot)

    else:
        # Generate next question
        state = await generate_question(state)
        if not state.get("errors"):
            next_q = state["quiz_context"].get("current_question")
            session.current_question = next_q
            if next_q:
                next_question_data = {
                    "question_number": question_number + 1,
                    "difficulty": state["quiz_context"]["current_difficulty"],
                    "question": next_q.get("question", ""),
                    "options": next_q.get("options", []),
                }

    await db.flush()

    # Log behavior
    try:
        await behavior_logs_collection().insert_one({
            "user_id": user.id,
            "event_type": "quiz_answer",
            "session_id": session_id,
            "question_number": question_number,
            "score": float(evaluation.get("score", 0)),
            "response_time": data.response_time_sec,
            "is_correct": bool(evaluation.get("is_correct", False)),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception:
        pass

    return QuizAnswerResponse(
        is_correct=bool(evaluation.get("is_correct", False)),
        score=float(evaluation.get("score", 0)),
        feedback=evaluation.get("feedback", ""),
        next_question=next_question_data,
        quiz_complete=quiz_complete,
    )


async def get_quiz_report(
    session_id: str,
    user: User,
    db: AsyncSession,
) -> QuizReportResponse:
    """Get the final report for a completed quiz session."""
    result = await db.execute(
        select(QuizSession).where(
            QuizSession.id == session_id,
            QuizSession.user_id == user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise QuizError("Quiz session not found")

    # Get all answer scores
    ans_result = await db.execute(
        select(QuizAnswer).where(QuizAnswer.session_id == session_id)
    )
    answers = ans_result.scalars().all()
    scores = [a.score for a in answers]

    return QuizReportResponse(
        session_id=session.id,
        total_questions=session.total_questions,
        avg_score=session.avg_score,
        avg_response_time=session.avg_response_time,
        scores=scores,
        final_report=session.final_report,
        skill_vector=user.skill_vector,
        qabil_score=user.qabil_score,
    )
