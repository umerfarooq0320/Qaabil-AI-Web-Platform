"""
Coach Agent (Rahnuma) prompts — voice and text coaching.
"""

SYSTEM_PROMPT = """You are Rahnuma, the AI coach for the QABIL platform.
You analyze speech and writing to provide actionable feedback on communication skills.
You are encouraging but honest. You speak in simple, clear language.
You must always return valid JSON with no extra text."""


def analyze_voice_prompt(transcript: str, user_profile: dict) -> str:
    return f"""
User Profile:
- Education: {user_profile.get('education', 'unknown')}
- English Level: {user_profile.get('english_level', 'medium')}

Voice Transcript:
\"{transcript}\"

Analyze this speech for:
1. Hesitation (pauses, incomplete thoughts)
2. Filler words ("umm", "like", "you know")
3. Grammar issues
4. Clarity and structure
5. Confidence level

Return ONLY valid JSON:
{{
  "hesitation_count": 3,
  "filler_words": ["umm", "like"],
  "grammar_issues": ["subject-verb agreement in line 2"],
  "clarity_score": 0.65,
  "confidence_score": 0.50,
  "tone": "uncertain",
  "feedback": "You speak clearly but hesitate before complex sentences. Try shorter structured responses.",
  "improvement_tips": ["Practice speaking in shorter sentences", "Pause deliberately instead of using fillers"],
  "overall_communication_score": 0.58
}}
"""


def coach_feedback_prompt(
    user_profile: dict,
    recent_performance: dict,
    area: str,
) -> str:
    return f"""
User Profile: {user_profile}
Recent Performance: {recent_performance}
Focus Area: {area}

Generate a short, motivating coaching message.
Include:
1. What improved
2. What still needs work
3. One specific exercise to try

Return ONLY valid JSON:
{{
  "message": "Great job! You improved your logical reasoning by 12%...",
  "improvement_noted": "logical_reasoning +12%",
  "focus_needed": "communication",
  "exercise": "Record yourself explaining a concept for 2 minutes"
}}
"""
