"""
SQLAlchemy Database Models

Defines the core entities: User, Resume, and Analysis.
"""

from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class User(Base):
    """User account for authentication and ownership."""
    
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Resume(Base):
    """Uploaded resume with extracted and parsed content."""
    
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    content_text = Column(Text)  # Raw extracted text from PDF
    parsed_data = Column(JSON)   # Structured data from AI parsing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resume(id={self.id}, filename={self.filename})>"


class Analysis(Base):
    """Job analysis result with match score and generated content."""
    
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Job information
    job_description = Column(Text, nullable=False)
    job_url = Column(String(2048))
    
    # Analysis results
    match_score = Column(Float)  # 0-100 percentage
    skill_gaps = Column(JSON)    # List of missing/weak skills
    suggestions = Column(JSON)   # Resume improvement suggestions
    
    # Generated content
    cold_email = Column(Text)
    linkedin_dm = Column(Text)
    interview_questions = Column(JSON)  # List of likely interview questions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="analyses")
    resume = relationship("Resume", back_populates="analyses")

    def __repr__(self):
        return f"<Analysis(id={self.id}, match_score={self.match_score})>"
