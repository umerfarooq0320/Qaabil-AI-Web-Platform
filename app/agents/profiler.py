"""
Profiler Agent — builds and updates User Intelligence Profiles.

Runs after:
- Quiz completion (initial profile)
- Task completion (profile update)
- Voice session (communication update)
"""

import logging
from app.agents.state import UserState
from app.agents.prompts.profiler_prompts import (
    SYSTEM_PROMPT,
    build_profile_prompt,
    generate_learning_path_prompt,
)
from app.core.llm import llm_json_query

logger = logging.getLogger(__name__)


async def build_intelligence_profile(state: UserState) -> UserState:
    """
    Build or update the User Intelligence Profile.

    Reads: profile, skill_vector, quiz history, task history
    Writes: state with intelligence_profile data
    """
    profile = state.get("profile", {})
    skill_vector = state.get("skill_vector", {})

    # Gather historical data
    quiz_ctx = state.get("quiz_context", {})
    quiz_history = []
    if quiz_ctx:
        quiz_history = [
            {
                "scores": quiz_ctx.get("scores", []),
                "times": quiz_ctx.get("response_times", []),
                "difficulty": quiz_ctx.get("current_difficulty", "medium"),
            }
        ]

    task_ctx = state.get("task_context", {})
    task_history = []
    if task_ctx and task_ctx.get("evaluation"):
        task_history = [task_ctx["evaluation"]]

    prompt = build_profile_prompt(profile, skill_vector, quiz_history, task_history)
    try:
        intelligence_profile = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)
    except Exception:
        intelligence_profile = None

    if intelligence_profile is None:
        logger.error("LLM failed, using fallback intelligence profile.")
        intelligence_profile = {
            "cognitive_ability": "Average",
            "learning_velocity": "Average",
            "consistency_score": "Average",
            "behavioral_traits": ["Diligent", "Curious"],
            "career_fit_predictions": ["Analyst", "Developer"],
        }

    state["intelligence_profile"] = intelligence_profile
    state["last_agent"] = "profiler"
    state["current_stage"] = "active"  # Move past onboarding

    return state


async def generate_learning_path(state: UserState) -> dict:
    """
    Generate a personalized learning path.

    Returns the learning path dict (not modifying state directly,
    since this is called from the API service layer).
    """
    skill_vector = state.get("skill_vector", {})
    intelligence_profile = state.get("intelligence_profile", {})
    progress = state.get("progress_history", [])

    # Summarize past performance
    past_performance = progress[-10:] if progress else []

    prompt = generate_learning_path_prompt(skill_vector, intelligence_profile, past_performance)
    learning_path = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if learning_path is None:
        return {
            "error": "Failed to generate learning path",
            "skill_gaps": [],
            "learning_path": [],
            "ai_reasoning": "Unable to generate at this time.",
        }

    return learning_path
