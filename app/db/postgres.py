"""
Async PostgreSQL connection using SQLAlchemy 2.0.
Provides session factory for dependency injection.
"""
import os
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

# --- URL FIX FOR RENDER/SUPABASE ---
# Pehle DATABASE_URL check karein (jo Render par hai), warna settings wala use karein
raw_url = os.getenv("DATABASE_URL") or settings.POSTGRES_URL

if not raw_url:
    raise ValueError("Database URL not found! Make sure DATABASE_URL is set in Render Environment.")

# Render/Supabase ke postgres:// ko postgresql+asyncpg:// mein convert karein
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif raw_url.startswith("postgresql://") and "+asyncpg" not in raw_url:
    raw_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine
engine_kwargs = {"echo": settings.DEBUG}
if "postgresql" in raw_url:
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(
    raw_url,
    **engine_kwargs
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for all ORM models
class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    """Dependency: yields an async DB session, auto-closes after request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        # Tables create karne se pehle logging ke liye engine check
        print(f"📡 Connecting to Database at: {engine.url.render_as_string(hide_password=True)}")
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """Dispose engine on shutdown."""
    await engine.dispose()