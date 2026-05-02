"""
Assessor Agent — generates adaptive quiz questions and evaluates answers.

This is the first agent a new user encounters.
It runs the adaptive quiz loop:
  Question → Answer → Evaluate → Adjust Difficulty → Next Question
"""

import logging
from app.agents.state import UserState
from app.agents.prompts.assessor_prompts import (
    SYSTEM_PROMPT,
    generate_question_prompt,
    evaluate_answer_prompt,
    final_report_prompt,
)
from app.core.llm import llm_json_query

logger = logging.getLogger(__name__)


async def generate_question(state: UserState) -> UserState:
    """
    Generate the next adaptive question based on current performance.

    Reads: profile, quiz_context (difficulty, scores)
    Writes: quiz_context.current_question
    """
    profile = state.get("profile", {})
    quiz_ctx = state.get("quiz_context", {})
    difficulty = quiz_ctx.get("current_difficulty", "medium")
    q_number = quiz_ctx.get("questions_asked", 0) + 1

    prompt = generate_question_prompt(profile, difficulty, q_number)
    question = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if question is None:
        # Retry once
        logger.warning("Assessor: question generation failed, retrying...")
        question = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if question is None:
        state["errors"] = state.get("errors", []) + ["Failed to generate question"]
        return state

    quiz_ctx["current_question"] = question
    state["quiz_context"] = quiz_ctx
    state["last_agent"] = "assessor"

    return state


async def evaluate_answer(state: UserState, user_answer: str, response_time: float) -> UserState:
    """
    Evaluate a user's answer and update skill tracking.

    Reads: quiz_context.current_question
    Writes: quiz_context.scores, quiz_context.current_difficulty
    """
    quiz_ctx = state.get("quiz_context", {})
    question = quiz_ctx.get("current_question", {})

    if not question:
        state["errors"] = state.get("errors", []) + ["No current question to evaluate"]
        return state

    prompt = evaluate_answer_prompt(
        question.get("question", ""),
        question.get("correct_answer", ""),
        user_answer,
    )
    result = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if result is None:
        state["errors"] = state.get("errors", []) + ["Failed to evaluate answer"]
        return state

    # Parse score safely
    try:
        score = float(result.get("score", 0))
    except (ValueError, TypeError):
        score = 0.0

    # Update quiz context
    scores = quiz_ctx.get("scores", [])
    scores.append(score)
    times = quiz_ctx.get("response_times", [])
    times.append(response_time)

    quiz_ctx["scores"] = scores
    quiz_ctx["response_times"] = times
    quiz_ctx["questions_asked"] = quiz_ctx.get("questions_asked", 0) + 1

    # Adaptive difficulty adjustment
    avg_score = sum(scores) / len(scores) if scores else 5.0
    if avg_score < 4:
        quiz_ctx["current_difficulty"] = "easy"
    elif avg_score < 7:
        quiz_ctx["current_difficulty"] = "medium"
    else:
        quiz_ctx["current_difficulty"] = "hard"

    # Check if quiz is complete
    max_q = quiz_ctx.get("max_questions", 5)
    if quiz_ctx["questions_asked"] >= max_q:
        quiz_ctx["is_complete"] = True

    quiz_ctx["last_evaluation"] = result
    state["quiz_context"] = quiz_ctx
    state["last_agent"] = "assessor"

    return state


async def generate_final_report(state: UserState) -> UserState:
    """
    Generate the final performance report after quiz completion.

    Reads: profile, quiz_context (scores, times)
    Writes: skill_vector (initial Qabil Score)
    """
    profile = state.get("profile", {})
    quiz_ctx = state.get("quiz_context", {})
    scores = quiz_ctx.get("scores", [])
    times = quiz_ctx.get("response_times", [])

    avg_time = sum(times) / len(times) if times else 0.0

    prompt = final_report_prompt(profile, scores, avg_time)
    report = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if report is None:
        state["errors"] = state.get("errors", []) + ["Failed to generate final report"]
        return state

    # Build skill vector from report
    skill_vector = {
        "logical_reasoning": float(report.get("logical_reasoning", 0.0)),
        "communication": float(report.get("communication", 0.0)),
        "confidence": float(report.get("confidence", 0.0)),
        "learning_speed": report.get("learning_speed", "medium"),
        "hidden_strength": report.get("hidden_strength", ""),
        "risk_area": report.get("risk_area", ""),
    }

    state["skill_vector"] = skill_vector
    state["quiz_context"]["final_report"] = report
    state["last_agent"] = "assessor"
    state["messages"] = state.get("messages", []) + [
        f"Quiz complete! Your level: {report.get('level', 'Unknown')}"
    ]

    return state


def get_initial_difficulty(education: str) -> str:
    """Determine starting difficulty from education level."""
    edu = education.lower() if education else "college"
    if edu in ("school", "primary", "secondary"):
        return "easy"
    elif edu in ("college", "intermediate", "bachelors"):
        return "medium"
    else:
        return "hard"
