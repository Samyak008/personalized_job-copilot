"""
ApplyWise API - FastAPI Application Entry Point

Main application configuration with CORS, exception handlers, and router setup.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.core.config import settings

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id

# Configure loguru with Correlation ID
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <magenta>[req:{extra[request_id]}]</magenta> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    filter=lambda record: record["extra"].update(request_id=correlation_id.get() or "N/A"),
)

app = FastAPI(
    title="ApplyWise API",
    description="AI Job Application Copilot - Analyze resumes, identify skill gaps, and generate personalized outreach content.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Middleware (Must be last to handle OPTIONS correctly before correlation middleware?)
# Actually correlation middleware should best be first to catch everything.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Tracing Middleware
app.add_middleware(CorrelationIdMiddleware)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ApplyWise API",
        "version": "0.1.0",
        "docs": "/api/docs",
    }


from app.api import api_router

app.include_router(api_router, prefix="/api/v1")


logger.info("ApplyWise API initialized")
