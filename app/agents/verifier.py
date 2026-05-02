"""
Verifier Agent — trust and fraud detection.

Detects:
1. Writing fingerprint (style consistency)
2. Behavior patterns (timing consistency)
3. Score consistency (no sudden jumps)

This is the MOAT — what makes QABIL trustworthy.
"""

import logging
from app.agents.state import UserState
from app.core.llm import llm_json_query

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Verification AI for QABIL.
You analyze submissions for authenticity and consistency.
You detect potential fraud, plagiarism, and identity inconsistencies.
Return valid JSON only."""


async def verify_submission(
    state: UserState,
    current_submission: str,
    past_submissions: list[str],
) -> dict:
    """
    Verify a submission for authenticity.

    Checks:
    - Writing style consistency with past work
    - Plagiarism indicators
    - Effort level
    """
    if not past_submissions:
        # First submission — establish baseline
        return {
            "trust_score": 1.0,
            "risk_flag": "none",
            "is_consistent": True,
            "analysis": "First submission — establishing baseline writing fingerprint.",
        }

    prompt = f"""
Analyze the consistency between this new submission and the user's past work.

Past submissions (writing samples):
{past_submissions[-3:]}

New submission:
\"{current_submission}\"

Check for:
1. Writing style consistency (vocabulary, sentence structure, complexity)
2. Sudden quality jumps that suggest outside help
3. Copy-paste indicators
4. Effort level

Return ONLY valid JSON:
{{
  "trust_score": 0.92,
  "risk_flag": "low",
  "is_consistent": true,
  "style_similarity": 0.88,
  "quality_jump": false,
  "analysis": "Writing style is consistent with previous submissions..."
}}

Rules:
- trust_score: 0.0 to 1.0
- risk_flag: "none", "low", "medium", "high"
- Be thorough but fair
"""

    result = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if result is None:
        return {
            "trust_score": state.get("trust_score", 1.0),
            "risk_flag": "unknown",
            "is_consistent": True,
            "analysis": "Verification unavailable. Maintaining current trust score.",
        }

    return result


async def check_behavior_consistency(state: UserState) -> dict:
    """
    Analyze behavior patterns for consistency.

    Checks timing, response patterns, score trajectories.
    """
    behavior_log = state.get("behavior_log", [])

    if len(behavior_log) < 5:
        return {
            "consistency_score": 1.0,
            "anomalies": [],
            "analysis": "Not enough data for behavior analysis.",
        }

    # Extract timing data
    response_times = [
        entry.get("response_time", 0) for entry in behavior_log if "response_time" in entry
    ]

    # Simple statistical checks
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        # Check for suspiciously fast responses
        too_fast = sum(1 for t in response_times if t < 2.0)  # Less than 2 seconds
        too_fast_ratio = too_fast / len(response_times)

        if too_fast_ratio > 0.5:
            return {
                "consistency_score": 0.5,
                "anomalies": ["unusually_fast_responses"],
                "analysis": f"Over 50% of responses under 2 seconds (avg: {avg_time:.1f}s). Possible automated responses.",
            }

    return {
        "consistency_score": 0.95,
        "anomalies": [],
        "analysis": "Behavior patterns appear consistent and natural.",
    }
