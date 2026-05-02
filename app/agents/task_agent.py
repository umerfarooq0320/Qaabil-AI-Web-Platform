"""
Task Agent — generates proof-of-work tasks and evaluates submissions.
"""

import logging
from app.agents.state import UserState
from app.agents.prompts.task_prompts import (
    SYSTEM_PROMPT,
    generate_task_prompt,
    evaluate_submission_prompt,
)
from app.core.llm import llm_json_query

logger = logging.getLogger(__name__)


async def generate_task(
    state: UserState,
    career_interest: str = "",
    past_tasks: list | None = None,
) -> dict:
    """
    Generate a new real-world task based on user's skill level.

    Returns task dict with title, description, rubric.
    """
    skill_vector = state.get("skill_vector", {})

    # Determine difficulty from skill level
    avg_skill = 0.5
    if skill_vector:
        numeric_skills = [v for v in skill_vector.values() if isinstance(v, (int, float))]
        if numeric_skills:
            avg_skill = sum(numeric_skills) / len(numeric_skills)

    if avg_skill < 0.35:
        difficulty = "easy"
    elif avg_skill < 0.65:
        difficulty = "medium"
    else:
        difficulty = "hard"

    prompt = generate_task_prompt(
        skill_vector,
        career_interest,
        difficulty,
        past_tasks or [],
    )
    task = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if task is None:
        return {
            "title": "Write a short paragraph about your skills",
            "description": "Write 100-200 words describing your top skills and how you would use them in a job.",
            "difficulty": difficulty,
            "task_type": "writing",
            "evaluation_rubric": {
                "clarity": "0-10",
                "structure": "0-10",
                "originality": "0-10",
                "effort": "0-10",
            },
        }

    return task


async def evaluate_task_submission(
    task_data: dict,
    submission: str,
) -> dict:
    """
    Evaluate a user's task submission against the rubric.

    Returns evaluation dict with scores and feedback.
    """
    rubric = task_data.get("evaluation_rubric", {})

    prompt = evaluate_submission_prompt(task_data, submission, rubric)
    evaluation = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if evaluation is None:
        return {
            "total_score": 5.0,
            "feedback": "Submission received. Manual review may be needed.",
            "is_genuine": True,
            "plagiarism_risk": "unknown",
        }

    return evaluation
