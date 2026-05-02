"""
API client for communicating with the QABIL FastAPI backend.
All frontend pages use this module to make API calls.
"""

import requests
import streamlit as st
from typing import Any

# Backend URL — change if deployed elsewhere
BASE_URL = "http://localhost:8000/api/v1"


def _get_headers() -> dict:
    """Get auth headers from session state."""
    token = st.session_state.get("access_token", "")
    if token:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return {"Content-Type": "application/json"}


def _handle_response(resp: requests.Response) -> dict | None:
    """Parse response, show errors via st.toast if any."""
    if resp.status_code == 200:
        return resp.json()
    else:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        st.error(f"❌ API Error ({resp.status_code}): {detail}")
        return None


# ──────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────

def signup(email: str, name: str, password: str, education: str = "", field: str = "", english: str = "") -> dict | None:
    """Register a new user."""
    payload = {
        "email": email,
        "name": name,
        "password": password,
        "education_level": education or None,
        "field_of_study": field or None,
        "english_level": english or None,
    }
    resp = requests.post(f"{BASE_URL}/auth/signup", json=payload)
    return _handle_response(resp)


def login(email: str, password: str) -> dict | None:
    """Login and get JWT token."""
    payload = {"email": email, "password": password}
    resp = requests.post(f"{BASE_URL}/auth/login", json=payload)
    return _handle_response(resp)


# ──────────────────────────────────────────────
# Profile
# ──────────────────────────────────────────────

def get_profile() -> dict | None:
    """Get current user's profile."""
    resp = requests.get(f"{BASE_URL}/profile/me", headers=_get_headers())
    return _handle_response(resp)


def update_profile(data: dict) -> dict | None:
    """Update user profile."""
    resp = requests.patch(f"{BASE_URL}/profile/me", json=data, headers=_get_headers())
    return _handle_response(resp)


def get_learning_path() -> dict | None:
    """Get AI-generated learning path."""
    resp = requests.get(f"{BASE_URL}/profile/learning-path", headers=_get_headers())
    return _handle_response(resp)


# ──────────────────────────────────────────────
# Quiz
# ──────────────────────────────────────────────

def start_quiz(num_questions: int = 5) -> dict | None:
    """Start a new adaptive quiz session."""
    resp = requests.post(
        f"{BASE_URL}/quiz/start",
        json={"num_questions": num_questions},
        headers=_get_headers(),
    )
    return _handle_response(resp)


def submit_answer(session_id: str, answer: str, response_time: float) -> dict | None:
    """Submit a quiz answer."""
    payload = {"user_answer": answer, "response_time_sec": response_time}
    resp = requests.post(
        f"{BASE_URL}/quiz/{session_id}/answer",
        json=payload,
        headers=_get_headers(),
    )
    return _handle_response(resp)


def get_quiz_report(session_id: str) -> dict | None:
    """Get quiz final report."""
    resp = requests.get(f"{BASE_URL}/quiz/{session_id}/report", headers=_get_headers())
    return _handle_response(resp)


# ──────────────────────────────────────────────
# Tasks
# ──────────────────────────────────────────────

def generate_task(career_interest: str = "") -> dict | None:
    """Generate a new AI task."""
    payload = {"career_interest": career_interest or None}
    resp = requests.post(f"{BASE_URL}/tasks/generate", json=payload, headers=_get_headers())
    return _handle_response(resp)


def submit_task(task_id: str, submission: str) -> dict | None:
    """Submit a task for evaluation."""
    payload = {"submission": submission}
    resp = requests.post(f"{BASE_URL}/tasks/{task_id}/submit", json=payload, headers=_get_headers())
    return _handle_response(resp)


def get_task_history() -> list | None:
    """Get all tasks."""
    resp = requests.get(f"{BASE_URL}/tasks/history", headers=_get_headers())
    return _handle_response(resp)


# ──────────────────────────────────────────────
# Coach
# ──────────────────────────────────────────────

def analyze_voice(transcript: str) -> dict | None:
    """Send transcript for voice analysis."""
    resp = requests.post(f"{BASE_URL}/coach/voice", json={"transcript": transcript}, headers=_get_headers())
    return _handle_response(resp)


def get_coaching(area: str = "general") -> dict | None:
    """Get coaching feedback."""
    resp = requests.post(f"{BASE_URL}/coach/feedback", json={"area": area}, headers=_get_headers())
    return _handle_response(resp)


# ──────────────────────────────────────────────
# Career
# ──────────────────────────────────────────────

def get_career_passport() -> dict | None:
    """Get career passport."""
    resp = requests.get(f"{BASE_URL}/career/passport", headers=_get_headers())
    return _handle_response(resp)


def get_job_matches() -> dict | None:
    """Get matched jobs."""
    resp = requests.get(f"{BASE_URL}/career/jobs", headers=_get_headers())
    return _handle_response(resp)
