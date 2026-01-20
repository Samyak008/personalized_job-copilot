import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.resume_parser import parse_resume, ParsedResumeData

@pytest.mark.asyncio
async def test_parse_resume_success():
    # Mock return value from agent
    mock_run_result = MagicMock()
    mock_run_result.output = """
    {
        "name": "John Doe",
        "email": "john@example.com",
        "skills": ["Python", "FastAPI"],
        "experience": [],
        "education": []
    }
    """
    
    with patch("app.agents.resume_parser.resume_parser_agent.run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_run_result
        
        result = await parse_resume("some raw text")
        
        assert isinstance(result, ParsedResumeData)
        assert result.name == "John Doe"
        assert "Python" in result.skills

@pytest.mark.asyncio
async def test_parse_resume_json_parsing_retry():
    # Test markdown block stripping
    mock_run_result = MagicMock()
    mock_run_result.output = """
    Here is the JSON:
    ```json
    {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "skills": ["React"],
        "experience": [],
        "education": []
    }
    ```
    """
    
    with patch("app.agents.resume_parser.resume_parser_agent.run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_run_result
        
        result = await parse_resume("text")
        assert result.name == "Jane Smith"

@pytest.mark.asyncio
async def test_parse_resume_failure():
    with patch("app.agents.resume_parser.resume_parser_agent.run", new_callable=AsyncMock) as mock_run:
        mock_run.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            await parse_resume("text")
