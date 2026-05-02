"""
Career Agent prompts — passport generation and job matching.
"""

SYSTEM_PROMPT = """You are the Career Intelligence AI for the QABIL platform.
You build career passports and match users with jobs based on their verified skills.
Focus on Pakistan's job market but include remote/international opportunities.
You must always return valid JSON with no extra text."""


def generate_passport_prompt(
    user_profile: dict,
    skill_vector: dict,
    intelligence_profile: dict,
    work_proofs: list,
    trust_score: float,
) -> str:
    return f"""
User Profile: {user_profile}
Skill Vector: {skill_vector}
Intelligence Profile: {intelligence_profile}
Work Proofs (task scores): {work_proofs}
Trust Score: {trust_score}

Generate a comprehensive Career Passport.

Return ONLY valid JSON:
{{
  "qabil_score": 72,
  "communication_rating": "B+",
  "ai_summary": "This candidate shows strong analytical ability, moderate communication, high consistency. Recommended for junior analyst roles.",
  "top_skills": ["logical reasoning", "pattern recognition"],
  "growth_areas": ["verbal communication", "confidence"],
  "recommended_roles": ["Junior Data Analyst", "Content Reviewer", "Research Assistant"],
  "readiness_level": "developing"
}}
"""


def match_jobs_prompt(
    skill_vector: dict,
    career_passport: dict,
    available_jobs: list,
) -> str:
    return f"""
Candidate Skill Vector: {skill_vector}
Career Passport Summary: {career_passport}

Available Jobs:
{available_jobs}

Match the candidate to the most suitable jobs.

Return ONLY valid JSON:
{{
  "matches": [
    {{
      "title": "Junior Data Analyst",
      "company": "TechCorp Lahore",
      "match_score": 0.85,
      "skill_fit": 0.90,
      "communication_fit": 0.75,
      "why_matched": "Strong analytical skills align with role requirements"
    }}
  ],
  "auto_resume_summary": "Motivated analytical thinker with proven problem-solving skills...",
  "auto_cover_letter": "Dear Hiring Manager, I am writing to express my interest..."
}}
"""
