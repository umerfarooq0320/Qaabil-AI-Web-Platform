"""
Custom exception classes for the QABIL application.
"""

from fastapi import HTTPException, status


class QabilException(HTTPException):
    """Base exception for QABIL-specific errors."""
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)


class AgentError(QabilException):
    """Raised when an AI agent fails to produce a valid result."""
    def __init__(self, agent_name: str, detail: str):
        super().__init__(
            detail=f"Agent '{agent_name}' error: {detail}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class QuizError(QabilException):
    """Raised for quiz-related errors."""
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class AuthError(QabilException):
    """Raised for authentication/authorization errors."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)
