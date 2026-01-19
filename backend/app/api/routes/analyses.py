"""
Analysis Routes

Endpoints for job analysis and content generation.
"""

from fastapi import APIRouter, Response, status
from typing import List
from uuid import UUID

from app.api.deps import SessionDep, CurrentUser
from app.services.analysis import AnalysisService
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisListResponse

router = APIRouter()


@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    request: AnalysisRequest,
    db: SessionDep,
    current_user: CurrentUser
):
    """
    Trigger a new analysis pipeline.
    This runs the Job Analyzer, Skill Gap Agent, Strategy Planner, and Content Generator.
    """
    analysis_service = AnalysisService(db)
    return await analysis_service.create_analysis(request, current_user)


@router.get("/", response_model=List[AnalysisListResponse])
async def list_analyses(
    db: SessionDep,
    current_user: CurrentUser
):
    """List all analyses for current user."""
    analysis_service = AnalysisService(db)
    return await analysis_service.list_analyses(current_user)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    db: SessionDep,
    current_user: CurrentUser
):
    """Get full details of a specific analysis."""
    analysis_service = AnalysisService(db)
    return await analysis_service.get_analysis(analysis_id, current_user)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: UUID,
    db: SessionDep,
    current_user: CurrentUser
):
    """Delete an analysis."""
    analysis_service = AnalysisService(db)
    await analysis_service.delete_analysis(analysis_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
