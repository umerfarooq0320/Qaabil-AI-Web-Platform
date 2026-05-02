"""
Auth endpoints — signup and login.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.schemas.user import UserSignup, UserLogin, AuthResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(data: UserSignup, db: AsyncSession = Depends(get_db)):
    """Create a new user account and return JWT token."""
    return await auth_service.signup(data, db)


@router.post("/login", response_model=AuthResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with email/password and return JWT token."""
    return await auth_service.login(data, db)
