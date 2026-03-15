"""
FastAPI application entry point for Exercise Form Feedback API.

This module initializes the FastAPI application, configures logging,
and sets up all routes and middleware.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Exercise Form Feedback API",
    description="AI-powered exercise form analysis using computer vision and LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS with environment-specific origins
allowed_origins = [
    "http://localhost:3000",  # Local development
]

# Add production frontend URL if provided
if settings.frontend_url:
    allowed_origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api/v1", tags=["Exercise Analysis"])


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Status message indicating the service is healthy
    """
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("=" * 50)
    logger.info("Exercise Form Feedback API Starting...")
    logger.info(f"Model: {settings.model_name}")
    logger.info(f"Max video size: {settings.max_video_size_mb}MB")
    logger.info(f"Max video duration: {settings.max_video_duration_sec}s")
    logger.info(f"Frame count: {settings.frame_count}")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information."""
    logger.info("Exercise Form Feedback API Shutting down...")
