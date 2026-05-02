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
        try:
            question = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)
        except Exception:
            question = None

    if question is None:
        logger.error("LLM failed entirely, using fallback question.")
        question = {
            "question": f"Fallback Question {q_number}: Which of the following is a primary color?",
            "options": ["Red", "Green", "Purple", "Orange"],
            "correct_answer": "Red",
            "explanation": "Red is one of the three primary colors.",
            "skill_tested": "general_knowledge"
        }

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
    try:
        result = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)
    except Exception:
        result = None

    if result is None:
        logger.error("LLM failed, using fallback evaluation.")
        is_correct = (user_answer.strip().lower() == question.get("correct_answer", "").strip().lower())
        result = {
            "is_correct": is_correct,
            "score": 10.0 if is_correct else 0.0,
            "feedback": "Fallback evaluation: The AI is currently unavailable.",
        }

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
    
    try:
        report = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)
    except Exception:
        report = None

    if report is None:
        logger.error("LLM failed, using fallback final report.")
        report = {
            "logical_reasoning": sum(scores)/len(scores) if scores else 5.0,
            "communication": 6.0,
            "confidence": 7.0,
            "level": "Intermediate",
            "learning_speed": "medium",
            "hidden_strength": "Resilience",
            "risk_area": "Needs more data",
            "performance_summary": "The AI is currently unavailable, so this is a fallback summary.",
            "improvement_tips": ["Keep practicing!"],
            "career_suggestion": "Generalist",
        }

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
