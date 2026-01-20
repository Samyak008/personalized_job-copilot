"""
Resume Parser Agent

Extracts structured data from raw resume text using AI.
Uses a manual JSON parsing approach for compatibility with free-tier OpenRouter models.
"""

import json
import re
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List, Optional, Union
from loguru import logger

from app.agents.base import get_llm_model, AGENT_RETRIES
from app.utils.file_extraction import extract_text_from_file, extract_text_from_upload


class Experience(BaseModel):
    """Work experience entry."""
    company: str = Field(..., description="Company or organization name")
    title: str = Field(..., description="Job title or role")
    duration: str = Field(..., description="Time period (e.g., 'Jan 2020 - Present')")
    description: Optional[str] = Field(default=None, description="Key responsibilities and achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies/tools used")


class Education(BaseModel):
    """Education entry."""
    institution: str = Field(..., description="School or university name")
    degree: str = Field(..., description="Degree type (e.g., 'Bachelor of Science')")
    field: str = Field(..., description="Field of study (e.g., 'Computer Science')")
    year: Optional[str] = Field(None, description="Graduation year or period")


class ParsedResumeData(BaseModel):
    """Complete structured resume data extracted by AI."""
    name: str = Field(..., description="Candidate's full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, State or Country")
    summary: Optional[str] = Field(None, description="Professional summary or objective")
    skills: List[str] = Field(default_factory=list, description="Technical and soft skills")
    experience: List[Experience] = Field(default_factory=list, description="Work experience")
    education: List[Education] = Field(default_factory=list, description="Education history")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    languages: List[str] = Field(default_factory=list, description="Languages spoken")


# JSON schema for the expected output format
JSON_SCHEMA = """{
  "name": "string (required)",
  "email": "string or null",
  "phone": "string or null",
  "location": "string or null",
  "summary": "string or null",
  "skills": ["array of strings"],
  "experience": [
    {
      "company": "string (required)",
      "title": "string (required)",
      "duration": "string (required)",
      "description": "string or null",
      "technologies": ["array of strings"]
    }
  ],
  "education": [
    {
      "institution": "string (required)",
      "degree": "string (required)",
      "field": "string (required)",
      "year": "string or null"
    }
  ],
  "certifications": ["array of strings"],
  "languages": ["array of strings"]
}"""


SYSTEM_PROMPT = f"""You are an expert resume parser. Your job is to extract structured information from resume text.

Instructions:
1. Extract ALL relevant information accurately
2. For skills, include both technical skills (Python, React) and soft skills (leadership, communication)
3. For experience, identify the company, title, duration, and key achievements
4. If information is not present or unclear, use null/empty values - do not make up data
5. Ensure dates and durations are formatted consistently
6. Extract technologies mentioned in job descriptions into the technologies field

IMPORTANT: You MUST respond with ONLY valid JSON. No markdown, no explanations, just pure JSON.

Use this exact structure:
{JSON_SCHEMA}

Be thorough but accurate. Only extract information that is explicitly stated in the resume."""


# Create the agent with string output (for free tier model compatibility)
resume_parser_agent = Agent(
    get_llm_model(),
    output_type=str,  # Use string output for free tier compatibility
    retries=AGENT_RETRIES,
    system_prompt=SYSTEM_PROMPT,
)


def _extract_json_from_response(response: str) -> dict:
    """
    Extract JSON from LLM response, handling markdown code blocks.
    
    Args:
        response: Raw LLM response that may contain JSON
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        ValueError: If no valid JSON could be extracted
    """
    # Try to extract JSON from markdown code blocks first
    json_patterns = [
        r'```json\s*\n?(.*?)\n?```',  # ```json ... ```
        r'```\s*\n?(.*?)\n?```',       # ``` ... ```
        r'\{.*\}',                      # Raw JSON object
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, response, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    # Last resort: try parsing the entire response
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from response: {response[:500]}")
        raise ValueError(f"Could not extract valid JSON from LLM response: {e}")


async def parse_resume(resume_text: str) -> ParsedResumeData:
    """
    Parse raw resume text into structured data.
    
    Args:
        resume_text: The raw text extracted from a resume PDF
        
    Returns:
        ParsedResumeData with structured resume information
        
    Raises:
        Exception: If parsing fails after retries
    """
    logger.info("Parsing resume with AI agent")
    logger.debug(f"Resume text length: {len(resume_text)} characters")
    
    try:
        result = await resume_parser_agent.run(
            f"Parse the following resume and extract all relevant information. Respond with ONLY valid JSON:\n\n{resume_text}"
        )
        
        # Extract and parse JSON from response
        raw_response = result.output
        logger.debug(f"Raw LLM response: {raw_response[:500]}...")
        
        json_data = _extract_json_from_response(raw_response)
        
        # Validate with Pydantic model
        parsed_data = ParsedResumeData.model_validate(json_data)
        
        logger.info(f"Resume parsed successfully. Found {len(parsed_data.skills)} skills, "
                   f"{len(parsed_data.experience)} experiences")
        
        return parsed_data
        
    except Exception as e:
        logger.error(f"Failed to parse resume: {e}")
        raise


async def parse_resume_file(file_content: bytes, filename: str) -> ParsedResumeData:
    """
    Parse a resume file (PDF or Word) directly.
    
    Args:
        file_content: Raw bytes of the file
        filename: Name of the file (used for type detection)
        
    Returns:
        ParsedResumeData with structured information
    """
    # Step 1: Extract text from file
    text_content = extract_text_from_file(file_content, filename)
    
    # Step 2: Parse text with AI agent
    return await parse_resume(text_content)
