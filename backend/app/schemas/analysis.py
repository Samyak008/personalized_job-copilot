"""
Pydantic Schemas for Analysis

Request/Response models for job analysis and generated content.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class SkillGap(BaseModel):
    """A skill gap identified in the analysis."""
    skill: str
    importance: str = Field(..., description="high, medium, or low")
    current_level: str = Field(default="none", description="none, basic, intermediate, or advanced")
    recommendation: str


class ImprovementAction(BaseModel):
    """An improvement action from strategy planning."""
    action: str
    priority: str = Field(..., description="immediate, short-term, or long-term")
    estimated_time: str


class AnalysisRequest(BaseModel):
    """Schema for creating a new analysis."""
    resume_id: UUID
    job_description: str = Field(..., min_length=50, description="Job description text (min 50 chars)")
    job_url: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Schema for analysis response with all generated content."""
    id: UUID
    resume_id: UUID
    job_description: str
    job_url: Optional[str] = None
    
    # Results
    match_score: float = Field(..., ge=0, le=100)
    skill_gaps: List[SkillGap] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    
    # Generated content
    cold_email: Optional[str] = None
    linkedin_dm: Optional[str] = None
    interview_questions: List[str] = Field(default_factory=list)
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    """Schema for analysis list item (lighter response)."""
    id: UUID
    resume_id: UUID
    match_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
