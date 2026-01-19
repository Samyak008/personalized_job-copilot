"""
Resume Service

Handles resume file processing, AI parsing, and storage.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException, status
from uuid import UUID
from typing import List

from app.db.repositories.base import BaseRepository
from app.db.models import Resume, User
from app.api.deps import CurrentUser
from app.agents import parse_resume_file  # Import our agent function
from app.utils.file_extraction import extract_text_from_file


class ResumeService:
    def __init__(self, db: AsyncSession):
        self.repo = BaseRepository(Resume, db)

    async def list_resumes(self, user: User) -> List[Resume]:
        """List all resumes for a user."""
        return await self.repo.get_by_user(user.id)

    async def get_resume(self, resume_id: UUID, user: User) -> Resume:
        """Get a specific resume owned by user."""
        resume = await self.repo.get(resume_id)
        if not resume or resume.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        return resume

    async def delete_resume(self, resume_id: UUID, user: User) -> bool:
        """Delete a resume owned by user."""
        # Verification handled by get_resume logic usually, but here checking generic exists
        resume = await self.repo.get(resume_id)
        if not resume or resume.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        return await self.repo.delete(resume_id)

    async def upload_resume(self, file: UploadFile, user: User) -> Resume:
        """
        Process an uploaded resume file:
        1. Read file content
        2. Extract text (for storage)
        3. Parse with AI Agent
        4. Save to Database
        """
        if not file.filename.endswith(('.pdf', '.docx', '.doc')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Please upload PDF or Word document."
            )

        content = await file.read()
        
        try:
            # 1. Extract raw text first (so we can save it even if AI fails, potentially?)
            # Actually our agent wrapper returns parsed data. But we might want raw text too.
            # parse_resume_file extracts text internally. 
            # We should probably use extract_text_from_file utility directly first to get text,
            # then pass text to parse_resume (agent).
            # But parse_resume_file is convenient. Let's use file extraction util here to save the raw text step.
            
            raw_text = extract_text_from_file(content, file.filename)
            
            # 2. Parse with AI
            # We can re-use raw_text if we call parse_resume(text) instead of parse_resume_file(bytes)
            from app.agents import parse_resume
            parsed_data = await parse_resume(raw_text)
            
            # 3. Create Resume Record
            resume = Resume(
                user_id=user.id,
                filename=file.filename,
                content_text=raw_text,
                parsed_data=parsed_data.model_dump(mode='json')
            )
            
            return await self.repo.create(resume)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process resume: {str(e)}"
            )
