"""
Pydantic Schemas for Resume

Request/Response models for resume upload and parsing.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any


class Experience(BaseModel):
    """Work experience entry."""
    company: str
    title: str
    duration: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry."""
    institution: str
    degree: str
    field: str
    year: Optional[str] = None


class ParsedResumeData(BaseModel):
    """Structured data extracted from resume by AI."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


class ResumeCreate(BaseModel):
    """Schema for resume creation (internal use)."""
    filename: str
    content_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None


class ResumeResponse(BaseModel):
    """Schema for resume response."""
    id: UUID
    filename: str
    parsed_data: Optional[ParsedResumeData] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    """Schema for resume list item (lighter response)."""
    id: UUID
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True
