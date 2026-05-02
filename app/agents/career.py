"""
Career Agent — builds career passport and matches jobs.
"""

import logging
from app.agents.state import UserState
from app.agents.prompts.career_prompts import (
    SYSTEM_PROMPT,
    generate_passport_prompt,
    match_jobs_prompt,
)
from app.core.llm import llm_json_query

logger = logging.getLogger(__name__)


async def build_career_passport(state: UserState, work_proofs: list) -> dict:
    """
    Generate a comprehensive career passport.

    Combines all user data into a recruiter-ready profile.
    """
    profile = state.get("profile", {})
    skill_vector = state.get("skill_vector", {})
    intelligence_profile = state.get("intelligence_profile", {})
    trust_score = state.get("trust_score", 1.0)

    prompt = generate_passport_prompt(
        profile, skill_vector, intelligence_profile, work_proofs, trust_score
    )
    passport = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if passport is None:
        return {
            "error": "Failed to generate career passport",
            "qabil_score": 0,
        }

    return passport


async def match_jobs(state: UserState, available_jobs: list | None = None) -> dict:
    """
    Match user to jobs based on their profile.

    If no jobs provided, generates sample matches based on profile.
    """
    skill_vector = state.get("skill_vector", {})

    # If no real jobs, create sample listings
    if not available_jobs:
        available_jobs = [
            {"title": "Junior Data Analyst", "company": "TechCorp", "requirements": "analytical skills, Excel, basic SQL"},
            {"title": "Content Writer", "company": "MediaHouse", "requirements": "writing skills, creativity, English proficiency"},
            {"title": "Customer Support Representative", "company": "CallCenter Plus", "requirements": "communication, patience, problem-solving"},
            {"title": "Research Assistant", "company": "University Lab", "requirements": "analytical thinking, attention to detail"},
            {"title": "Social Media Manager", "company": "BrandBoost", "requirements": "creativity, communication, content creation"},
        ]

    career_passport = {
        "skill_vector": skill_vector,
        "trust_score": state.get("trust_score", 1.0),
        "current_stage": state.get("current_stage", "developing"),
    }

    prompt = match_jobs_prompt(skill_vector, career_passport, available_jobs)
    matches = await llm_json_query(prompt, system_prompt=SYSTEM_PROMPT)

    if matches is None:
        return {
            "matches": [],
            "error": "Failed to match jobs",
        }

    return matches
