"""
Async MongoDB connection using Motor.
Used for behavior logs, voice sessions, and state snapshots.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()

# Motor async client
_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create the Motor client singleton."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
    return _client


def get_mongo_db():
    """Get the qabil database instance."""
    client = get_mongo_client()
    return client[settings.MONGODB_DB]


async def close_mongo():
    """Close the Motor client on shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


# ---- Collection accessors ----

def behavior_logs_collection():
    """Collection: tracks every user action (clicks, answers, logins)."""
    return get_mongo_db()["behavior_logs"]


def voice_sessions_collection():
    """Collection: stores voice transcripts and AI feedback."""
    return get_mongo_db()["voice_sessions"]


def user_state_snapshots_collection():
    """Collection: full UserState snapshots for audit trail."""
    return get_mongo_db()["user_state_snapshots"]
