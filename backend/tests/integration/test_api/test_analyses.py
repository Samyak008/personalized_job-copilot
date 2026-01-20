import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from app.schemas.analysis import AnalysisResponse, AnalysisListResponse
from typing import List

@pytest.fixture
def mock_analysis_service():
    with patch("app.api.routes.analyses.AnalysisService") as mock_cls:
        # Check if the code instantiates the class (it does: AnalysisService(db))
        # So we mock the instance returned by the constructor
        mock_instance = AsyncMock()
        mock_cls.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_create_analysis(client: AsyncClient, mock_analysis_service):
    # Setup
    resume_id = uuid4()
    analysis_id = uuid4()
    job_desc = "Looking for a senior python developer with FastAPI experience. " * 3
    
    expected_response = AnalysisResponse(
        id=analysis_id,
        resume_id=resume_id,
        job_description=job_desc,
        match_score=85.5,
        skill_gaps=[],
        suggestions=["Update header"],
        created_at=datetime.now(timezone.utc)
    )
    
    mock_analysis_service.create_analysis.return_value = expected_response

    # Execute
    payload = {
        "resume_id": str(resume_id),
        "job_description": job_desc
    }
    response = await client.post("/api/v1/analyses/", json=payload)

    # Verify
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == str(analysis_id)
    assert data["match_score"] == 85.5
    
    mock_analysis_service.create_analysis.assert_called_once()


@pytest.mark.asyncio
async def test_create_analysis_validation_error(client: AsyncClient, mock_analysis_service):
    # Short job description
    payload = {
        "resume_id": str(uuid4()),
        "job_description": "Too short"
    }
    response = await client.post("/api/v1/analyses/", json=payload)
    
    assert response.status_code == 422
    mock_analysis_service.create_analysis.assert_not_called()


@pytest.mark.asyncio
async def test_list_analyses(client: AsyncClient, mock_analysis_service):
    # Setup
    analysis_id = uuid4()
    resume_id = uuid4()
    expected_list = [
        AnalysisListResponse(
            id=analysis_id,
            resume_id=resume_id,
            match_score=90.0,
            created_at=datetime.now(timezone.utc)
        )
    ]
    mock_analysis_service.list_analyses.return_value = expected_list

    # Execute
    response = await client.get("/api/v1/analyses/")
    
    # Verify
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(analysis_id)
