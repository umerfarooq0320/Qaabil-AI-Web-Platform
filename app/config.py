"""
Application configuration loaded from environment variables.
Uses pydantic-settings for validation and type coercion.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # -- App --
    APP_NAME: str = "Qabil"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me"

    # -- PostgreSQL --
    POSTGRES_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/qabil"

    # -- MongoDB --
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "qabil"

    # -- Redis --
    REDIS_URL: str = "redis://localhost:6379/0"

    # -- AI / LLM --
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL: str = "meta-llama/llama-3-8b-instruct"

    # -- JWT --
    JWT_SECRET: str = "change-me-jwt"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance - loaded once per process."""
    return Settings()
