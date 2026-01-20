"""
Analysis Service

Business logic for running job analysis pipeline.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from uuid import UUID
from typing import List
import sys

from app.db.repositories.base import BaseRepository
from app.db.models import Analysis, Resume, User
from app.api.deps import CurrentUser
from app.schemas.analysis import AnalysisRequest
from app.agents import run_analysis_pipeline, PipelineResult


class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.repo = BaseRepository(Analysis, db)
        self.resume_repo = BaseRepository(Resume, db)

    async def list_analyses(self, user: User) -> List[Analysis]:
        """List all analyses for a user."""
        return await self.repo.get_by_user(user.id)

    async def get_analysis(self, analysis_id: UUID, user: User) -> Analysis:
        """Get a specific analysis."""
        analysis = await self.repo.get(analysis_id)
        if not analysis or analysis.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        return analysis

    async def delete_analysis(self, analysis_id: UUID, user: User) -> bool:
        """Delete an analysis."""
        analysis = await self.repo.get(analysis_id)
        if not analysis or analysis.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        return await self.repo.delete(analysis_id)

    async def create_analysis(self, request: AnalysisRequest, user: User) -> Analysis:
        """
        Run full analysis pipeline:
        1. Fetch resume text
        2. Run AI pipeline (Job Analyzer -> Skill Gap -> Strategy -> Content)
        3. Save results
        """
        # 1. Fetch Resume
        resume = await self.resume_repo.get(request.resume_id)
        if not resume or resume.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        if not resume.content_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume has no text content to analyze"
            )
            
        try:
            # 2. Run Pipeline
            # run_analysis_pipeline takes (resume_text, job_desc)
            # It runs all agents in parallel/sequence
            result: PipelineResult = await run_analysis_pipeline(
                resume_text=resume.content_text,
                job_description=request.job_description
            )
            
            # Map Agent Results to DB Model
            
            # Combine missing and weak skills for "skill_gaps"
            # We convert Pydantic models to dicts for JSON storage
            skill_gaps = [
                gap.model_dump() 
                for gap in (result.match_analysis.missing_skills + result.match_analysis.weak_skills)
            ]
            
            # 3. Create Analysis Record
            analysis = Analysis(
                user_id=user.id,
                resume_id=resume.id,
                job_description=request.job_description,
                job_url=request.job_url,
                
                match_score=result.match_analysis.match_score,
                skill_gaps=skill_gaps,
                suggestions=result.strategy.resume_improvements if result.strategy else [],
                
                cold_email=result.content.cold_email if result.content else None,
                linkedin_dm=result.content.linkedin_dm if result.content else None,
                interview_questions=result.content.interview_questions if result.content else []
            )
            
            return await self.repo.create(analysis)
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"CRITICAL PIPELINE ERROR:\n{error_trace}", file=sys.stderr)  # Force print to stderr
            
            # Log the full error here in a real app
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis pipeline failed: {str(e)}"
            )
