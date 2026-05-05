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
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting QABIL AI Platform...")
    
    # Init DB
    try:
        await init_db()
        logger.info("✅ Database connected successfully")
    except Exception as e:
        logger.error(f"❌ DB connection failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    await close_mongo()

app = FastAPI(
    title="QABIL AI Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — Final Fix for Deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount routes
app.include_router(v1_router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "app": "QABIL",
        "status": "online",
        "message": "Backend is talking to Frontend!"
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
