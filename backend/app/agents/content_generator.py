"""
Content Generator Agent

Generates professional networking content (emails, DMs) and interview prep materials.
"""

import json
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List
from loguru import logger

from app.agents.base import get_llm_model, AGENT_RETRIES
from app.agents.resume_parser import ParsedResumeData
from app.agents.job_analyzer import ParsedJobData
from app.agents.strategy_planner import ImprovementStrategy
from app.utils import extract_json_from_response


class GeneratedContent(BaseModel):
    """Content generated for job application."""
    cold_email: str = Field(..., description="Professional email to recruiter/hiring manager")
    linkedin_dm: str = Field(..., description="Short LinkedIn connection message")
    interview_questions: List[str] = Field(..., description="Potential interview questions with brief answer hints")
    elevator_pitch: str = Field(..., description="30-second introduction for the candidate")


JSON_SCHEMA = """{
  "cold_email": "string (markdown allowed)",
  "linkedin_dm": "string",
  "interview_questions": ["array of strings"],
  "elevator_pitch": "string"
}"""


SYSTEM_PROMPT = f"""You are an expert copywriter and career coach. Your goal is to write high-converting job application content.

Instructions:
1. Write a Cold Email that highlights the candidate's strengths relevant to the job. keep it professional but engaging.
2. Write a LinkedIn DM (max 300 chars) for connecting with the hiring manager.
3. Generate 5 likely Interview Questions based on the job requirements and candidate's gaps.
4. Create a concise Elevator Pitch.

IMPORTANT: Customize everything to the specific Job and Candidate.

You MUST respond with ONLY valid JSON. Use this structure:
{JSON_SCHEMA}
"""


content_agent = Agent(
    get_llm_model(),
    output_type=str,
    retries=AGENT_RETRIES,
    system_prompt=SYSTEM_PROMPT,
)


async def generate_content(
    resume_data: ParsedResumeData,
    job_data: ParsedJobData,
    strategy: ImprovementStrategy
) -> GeneratedContent:
    """
    Generate application content.
    
    Args:
        resume_data: Parsed resume
        job_data: Parsed job
        strategy: Improvement strategy (to highlight strengths/mitigate weaknesses)
        
    Returns:
        GeneratedContent: Emails, questions, etc.
    """
    logger.info("Generating application content")
    
    # Prepare input summary
    inputs = {
        "candidate_name": resume_data.name,
        "candidate_skills": resume_data.skills[:10],  # Top skills
        "target_role": job_data.title,
        "company": job_data.company,
        "key_requirements": [s.skill for s in job_data.required_skills[:5]],
        "focus_areas": strategy.interview_focus_areas
    }
    
    prompt = f"""Generate content for this application:

CONTEXT:
{json.dumps(inputs, indent=2)}

Generate the cold email, DM, interview questions, and pitch as valid JSON.
"""

    try:
        result = await content_agent.run(prompt)
        
        json_data = extract_json_from_response(result.output)
        content = GeneratedContent.model_validate(json_data)
        
        logger.info("Content generation complete")
        return content
        
    except Exception as e:
        logger.error(f"Failed to generate content: {e}")
        raise
