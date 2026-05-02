"""
Supervisor Agent — monitors engagement and triggers feedback loops.

Tracks:
- Time spent
- Inactivity
- Retries
- Drop-offs

Triggers:
- IF stuck → give hint
- IF inactive → send nudge
- IF improving → reward feedback
"""

import logging
from datetime import datetime, timezone
from app.agents.state import UserState
from app.core.llm import llm_json_query

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Supervisor AI for QABIL.
You monitor student engagement and decide when to intervene.
You are encouraging and proactive. Return valid JSON only."""


async def check_engagement(state: UserState) -> dict:
    """
    Analyze user behavior and decide on intervention.

    Returns action dict: nudge, hint, reward, or none.
    """
    behavior_log = state.get("behavior_log", [])
    skill_vector = state.get("skill_vector", {})
    trust_score = state.get("trust_score", 1.0)

    # Simple heuristics first (fast, no LLM needed)
    if not behavior_log:
        return {"action": "none", "message": "No behavior data yet"}

    recent = behavior_log[-10:]  # Last 10 actions

    # Check for patterns
    action_types = [entry.get("type", "") for entry in recent]

    # Inactivity detection (no actions in recent log)
    if len(recent) < 2:
        return {
            "action": "nudge",
            "message": "Hey! You haven't been active recently. Come back and continue your journey!",
            "trigger": "inactivity",
        }

    # Check for repeated failures
    failures = sum(1 for entry in recent if entry.get("score", 10) < 4)
    if failures > 3:
        return {
            "action": "hint",
            "message": "Looks like you're finding this challenging. Here's a tip: break the problem into smaller parts.",
            "trigger": "struggling",
        }

    # Check for improvement
    scores = [entry.get("score", 0) for entry in recent if "score" in entry]
    if len(scores) >= 3:
        trend = scores[-1] - scores[0]
        if trend > 2:
            return {
                "action": "reward",
                "message": f"Amazing progress! You've improved by {trend:.0f} points. Keep going! 🎉",
                "trigger": "improving",
            }

    return {"action": "none", "message": "User is progressing normally"}
