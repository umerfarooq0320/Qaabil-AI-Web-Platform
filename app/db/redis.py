"""
Redis connection for caching LLM responses and session data.
"""

import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

_redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Get or create the async Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis():
    """Close Redis connection on shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
