"""
Job Description Analyzer Agent

Extracts structured requirements from job descriptions using AI.
Uses manual JSON parsing for compatibility with free-tier OpenRouter models.
"""

import json
import re
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List, Optional
from loguru import logger

from app.agents.base import get_llm_model, AGENT_RETRIES


class RequiredSkill(BaseModel):
    """A skill mentioned in the job description."""
    skill: str = Field(..., description="Name of the skill")
    importance: str = Field(..., description="required, preferred, or nice-to-have")


class ParsedJobData(BaseModel):
    """Structured data extracted from a job description."""
    title: str = Field(..., description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    required_skills: List[RequiredSkill] = Field(default_factory=list, description="List of skills")
    required_experience_years: Optional[int] = Field(None, description="Minimum years of experience required")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities")
    salary_range: Optional[str] = Field(None, description="Salary range if mentioned")
    location: Optional[str] = Field(None, description="Job location")


# JSON schema for the expected output format
JSON_SCHEMA = """{
  "title": "string (required)",
  "company": "string or null",
  "required_skills": [
    {
      "skill": "string",
      "importance": "required | preferred | nice-to-have"
    }
  ],
  "required_experience_years": "integer or null",
  "responsibilities": ["array of strings"],
  "salary_range": "string or null",
  "location": "string or null"
}"""


SYSTEM_PROMPT = f"""You are an expert technical recruiter. Your job is to extract structured requirements from job descriptions.

Instructions:
1. Identify the job title and company accurately.
2. Extract ALL technical and soft skills mentioned.
3. Classify skill importance (required vs preferred) based on keywords like "must have", "bonus", "plus".
4. Extract key responsibilities as a concise list.
5. Identify minimum years of experience (return an integer, e.g., 5 for "5+ years").

IMPORTANT: You MUST respond with ONLY valid JSON. No markdown, no explanations, just pure JSON.

Use this exact structure:
{JSON_SCHEMA}
"""


# Create the agent
job_analyzer_agent = Agent(
    get_llm_model(),
    output_type=str,  # String output for manual parsing
    retries=AGENT_RETRIES,
    system_prompt=SYSTEM_PROMPT,
)


def _extract_json_from_response(response: str) -> dict:
    """Helper to extract JSON from LLM response (handling markdown)."""
    # Try to extract JSON from markdown code blocks first
    json_patterns = [
        r'```json\s*\n?(.*?)\n?```',
        r'```\s*\n?(.*?)\n?```',
        r'\{.*\}',
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, response, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    # Fallback: try parsing the whole string
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from response: {response[:500]}")
        raise ValueError(f"Could not extract valid JSON from LLM response: {e}")


async def analyze_job_description(job_text: str) -> ParsedJobData:
    """
    Analyze a job description and extract structured data.
    
    Args:
        job_text: Raw text of the job description
        
    Returns:
        ParsedJobData: Structured job requirements
    """
    logger.info("Analyzing job description with AI agent")
    
    try:
        result = await job_analyzer_agent.run(
            f"Analyze the following job description and extract requirements. Respond with ONLY valid JSON:\n\n{job_text}"
        )
        
        # Extract and parse JSON
        json_data = _extract_json_from_response(result.output)
        
        # Validate with Pydantic
        parsed_data = ParsedJobData.model_validate(json_data)
        
        logger.info(f"Job analyzed successfully: {parsed_data.title} "
                   f"({len(parsed_data.required_skills)} skills found)")
        
        return parsed_data
        
    except Exception as e:
        logger.error(f"Failed to analyze job description: {e}")
        raise
