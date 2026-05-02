"""
Assessor Agent prompts — generates adaptive questions and evaluates answers.
"""

SYSTEM_PROMPT = """You are an AI assessment expert for the QABIL platform.
Your job is to generate adaptive quiz questions that accurately measure a student's cognitive abilities.
You must always return valid JSON with no extra text."""


def generate_question_prompt(profile: dict, difficulty: str, question_number: int) -> str:
    return f"""
Student profile:
- Education: {profile.get('education', 'unknown')}
- Field: {profile.get('field', 'general')}
- English level: {profile.get('english_level', 'medium')}

Generate 1 logical reasoning question.

Difficulty: {difficulty}
Question number: {question_number}

Return ONLY valid JSON. Do NOT add any text before or after JSON.

{{
  "question": "the question text",
  "options": ["option A", "option B", "option C", "option D"],
  "correct_answer": "the correct option text",
  "explanation": "brief explanation of why this is correct",
  "skill_tested": "logical_reasoning"
}}
"""


def evaluate_answer_prompt(question: str, correct_answer: str, user_answer: str) -> str:
    return f"""
Question: {question}
Correct Answer: {correct_answer}
User Answer: {user_answer}

Evaluate if the user's answer is correct or partially correct.

Return ONLY valid JSON:
{{
  "score": 7,
  "is_correct": true,
  "feedback": "brief feedback for the student"
}}

Rules:
- score is 0-10 (integer)
- is_correct is true/false (boolean)
- feedback should be encouraging but honest
"""


def final_report_prompt(profile: dict, scores: list, avg_time: float) -> str:
    return f"""
Student profile: {profile}
Scores across questions: {scores}
Average response time: {avg_time:.1f} seconds

Analyze the student's performance and generate a comprehensive report.

Return ONLY valid JSON:
{{
  "performance_summary": "2-line summary of overall performance",
  "level": "Beginner or Intermediate or Advanced",
  "logical_reasoning": 0.78,
  "communication": 0.42,
  "confidence": 0.35,
  "learning_speed": "slow or medium or fast",
  "hidden_strength": "one key strength discovered",
  "risk_area": "one area needing improvement",
  "career_suggestion": "suggested career direction",
  "improvement_tips": ["tip 1", "tip 2", "tip 3"]
}}

Rules:
- All float scores between 0.0 and 1.0
- Be specific and actionable
- Consider response time as a signal for confidence
"""
