"""
API Router

Aggregates all API routes (Auth, Resume, Analysis).
"""

from fastapi import APIRouter

from app.api.routes import resumes, analyses

api_router = APIRouter()

api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
