"""
Profiler Agent prompts — builds and updates user intelligence profiles.
"""

SYSTEM_PROMPT = """You are an AI profiler for the QABIL platform.
You analyze user data to build comprehensive intelligence profiles that track cognitive ability,
communication skills, behavioral traits, and career potential.
You must always return valid JSON with no extra text."""


def build_profile_prompt(
    profile: dict,
    skill_vector: dict,
    quiz_history: list,
    task_history: list,
) -> str:
    return f"""
User Profile:
{profile}

Current Skill Vector:
{skill_vector}

Quiz History (scores and times):
{quiz_history}

Task History (submissions and scores):
{task_history}

Build a comprehensive User Intelligence Profile.

Return ONLY valid JSON:
{{
  "cognitive_ability": 0.72,
  "communication_skill": 0.45,
  "behavioral_traits": ["consistent", "analytical", "slow starter"],
  "learning_velocity": "medium",
  "consistency_score": 0.85,
  "career_fit_predictions": ["Data Analyst", "Content Writer"],
  "personality_indicators": ["detail-oriented", "prefers structured tasks"],
  "growth_trajectory": "upward",
  "recommended_focus": "communication improvement"
}}

Rules:
- Float scores between 0.0 and 1.0
- Be specific based on actual data patterns
- Identify non-obvious strengths
"""


def generate_learning_path_prompt(
    skill_vector: dict,
    intelligence_profile: dict,
    past_performance: list,
) -> str:
    return f"""
Current Skill Vector:
{skill_vector}

Intelligence Profile:
{intelligence_profile}

Past Performance Summary:
{past_performance}

Generate a personalized 5-day learning path.

Return ONLY valid JSON:
{{
  "skill_gaps": ["communication", "confidence"],
  "learning_path": [
    {{
      "day": 1,
      "tasks": ["5-min speaking task", "1 logical problem", "1 real-world scenario"],
      "focus_area": "communication basics",
      "estimated_time_min": 30
    }},
    {{
      "day": 2,
      "tasks": ["adjusted based on performance"],
      "focus_area": "logical reasoning",
      "estimated_time_min": 25
    }}
  ],
  "ai_reasoning": "Based on the skill gaps, this path prioritizes..."
}}

Rules:
- Each day should have 2-4 concrete tasks
- Difficulty should gradually increase
- Estimated time should be realistic (15-45 min/day)
- Focus on the weakest areas first
"""
