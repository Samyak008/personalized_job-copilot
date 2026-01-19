"""
Resume Routes

Endpoints for resume management.
"""

from fastapi import APIRouter, UploadFile, File, Response, status
from typing import List
from uuid import UUID

from app.api.deps import SessionDep, CurrentUser
from app.services.resume import ResumeService
from app.schemas.resume import ResumeResponse, ResumeListResponse

router = APIRouter()


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: SessionDep = None,  # Dependency injection
    current_user: CurrentUser = None
):
    """
    Upload a resume (PDF/Word).
    Autocratically parses text and extracts skills using AI.
    """
    resume_service = ResumeService(db)
    return await resume_service.upload_resume(file, current_user)


@router.get("/", response_model=List[ResumeListResponse])
async def list_resumes(
    db: SessionDep,
    current_user: CurrentUser
):
    """List all resumes for the current user."""
    resume_service = ResumeService(db)
    return await resume_service.list_resumes(current_user)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    db: SessionDep,
    current_user: CurrentUser
):
    """Get a specific resume with full parsed details."""
    resume_service = ResumeService(db)
    return await resume_service.get_resume(resume_id, current_user)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    db: SessionDep,
    current_user: CurrentUser
):
    """Delete a resume."""
    resume_service = ResumeService(db)
    await resume_service.delete_resume(resume_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
