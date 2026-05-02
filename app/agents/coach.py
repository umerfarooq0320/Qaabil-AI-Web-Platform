"""
Coach Agent (Rahnuma) — voice and text coaching.

Analyzes speech transcripts and provides feedback on:
- Hesitation
- Filler words
- Grammar
- Confidence
- Clarity
"""

import logging
from app.agents.state import UserState
from app.agents.prompts.coach_prompts import (
    SYSTEM_PROMPT,
    analyze_voice_prompt,
    coach_feedback_prompt,
)
from app.core.llm import llm_json_query

logger = logging.getLogger(__name__)


async def analyze_voice(state: UserState, transcript: str) -> dict:
    """
    Analyze a voice transcript for communication skills.

    Returns analysis dict with scores and feedback.
    """
    profile = state.get("profile", {})

    prompt = analyze_voice_prompt(transcript, profile)
    analysis = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if analysis is None:
        return {
            "error": "Failed to analyze voice",
            "feedback": "Unable to analyze at this time. Please try again.",
        }

    return analysis


async def get_coaching_feedback(state: UserState, area: str = "general") -> dict:
    """
    Generate personalized coaching feedback.

    Reads: profile, recent performance
    Returns: coaching message dict
    """
    profile = state.get("profile", {})
    skill_vector = state.get("skill_vector", {})
    recent_performance = {
        "skill_vector": skill_vector,
        "trust_score": state.get("trust_score", 1.0),
        "current_stage": state.get("current_stage", "onboarding"),
    }

    prompt = coach_feedback_prompt(profile, recent_performance, area)
    feedback = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if feedback is None:
        return {
            "message": "Keep going! Every step counts.",
            "focus_needed": area,
        }

    return feedback
