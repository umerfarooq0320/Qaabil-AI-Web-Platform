"""
Task Agent prompts — generates real-world tasks and evaluation rubrics.
"""

SYSTEM_PROMPT = """You are the Task Generator AI for the QABIL platform.
You create real-world tasks that test practical skills.
Tasks should be relevant to Pakistan's job market and economy.
You must always return valid JSON with no extra text."""


def generate_task_prompt(
    skill_vector: dict,
    career_interest: str,
    difficulty: str,
    past_tasks: list,
) -> str:
    return f"""
Student Skill Vector:
{skill_vector}

Career Interest: {career_interest or "general"}
Difficulty Level: {difficulty}
Past Tasks (titles): {[t.get('title', '') for t in past_tasks[-5:]]}

Generate a real-world task that:
1. Tests practical skills relevant to their career interest
2. Is completable in 15-30 minutes
3. Has clear evaluation criteria
4. Is different from past tasks

Return ONLY valid JSON:
{{
  "title": "Write a product description for a local business",
  "description": "A local clothing store in Lahore wants to sell online...",
  "difficulty": "{difficulty}",
  "task_type": "writing",
  "evaluation_rubric": {{
    "clarity": "Is the writing clear and easy to understand? (0-10)",
    "structure": "Is the content well-organized? (0-10)",
    "originality": "Does it show creative thinking? (0-10)",
    "relevance": "Is it relevant to the business? (0-10)",
    "effort": "Does it show genuine effort? (0-10)"
  }},
  "expected_time_min": 20,
  "skills_tested": ["communication", "creativity"]
}}
"""


def evaluate_submission_prompt(
    task: dict,
    submission: str,
    rubric: dict,
) -> str:
    return f"""
Task: {task.get('title', '')}
Description: {task.get('description', '')}

Evaluation Rubric:
{rubric}

Student Submission:
\"{submission}\"

Evaluate this submission against the rubric.

Return ONLY valid JSON:
{{
  "scores": {{
    "clarity": 7,
    "structure": 6,
    "originality": 8,
    "relevance": 7,
    "effort": 8
  }},
  "total_score": 7.2,
  "feedback": "Strong creative approach. Structure could be improved by...",
  "strengths": ["creative thinking", "relevant content"],
  "weaknesses": ["paragraph structure", "minor grammar issues"],
  "is_genuine": true,
  "plagiarism_risk": "low"
}}
"""
