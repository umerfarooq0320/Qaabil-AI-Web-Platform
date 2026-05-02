"""
QABIL AI Platform — FastAPI Application Entry Point

Start with:
    uvicorn app.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.router import router as v1_router
from app.db.postgres import init_db, close_db
from app.db.mongodb import close_mongo

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # ---- Startup ----
    logger.info("🚀 Starting QABIL AI Platform...")

    # Create database tables (use Alembic in production)
    try:
        await init_db()
        logger.info("✅ PostgreSQL connected & tables created")
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL init failed: {e}")
        logger.warning("   Server will start, but DB endpoints will fail.")
        logger.warning("   Make sure PostgreSQL is running and .env is configured.")

    logger.info("✅ QABIL backend is ready!")
    logger.info(f"📖 API Docs: http://localhost:8000/docs")

    yield

    # ---- Shutdown ----
    logger.info("Shutting down...")
    await close_db()
    await close_mongo()


# Create app
app = FastAPI(
    title="QABIL AI Platform",
    description=(
        "AI-native system for adaptive assessment, "
        "skill profiling, and career passport generation."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount v1 API routes
app.include_router(v1_router)


# Health check
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
