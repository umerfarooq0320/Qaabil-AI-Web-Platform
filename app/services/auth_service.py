"""
Auth Service — handles user registration and login.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserSignup, UserLogin, AuthResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import AuthError


async def signup(data: UserSignup, db: AsyncSession) -> AuthResponse:
    """Register a new user."""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise AuthError("Email already registered")

    # Create user
    user = User(
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
        education_level=data.education_level,
        field_of_study=data.field_of_study,
        english_level=data.english_level,
        current_stage="onboarding",
    )
    db.add(user)
    await db.flush()  # Get the ID without committing

    token = create_access_token(user.id)

    return AuthResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
    )


async def login(data: UserLogin, db: AsyncSession) -> AuthResponse:
    """Authenticate user and return JWT token."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise AuthError("Invalid email or password")

    token = create_access_token(user.id)

    return AuthResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
    )
