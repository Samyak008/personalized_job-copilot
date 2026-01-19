"""
Skill Gap Analysis Agent

Compares parsed resume data against job requirements to identify gaps.
Uses manual JSON parsing for compatibility with free-tier OpenRouter models.
"""

import json
import re
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List
from loguru import logger

from app.agents.base import get_llm_model, AGENT_RETRIES
from app.agents.resume_parser import ParsedResumeData
from app.agents.job_analyzer import ParsedJobData


class SkillGap(BaseModel):
    """Analysis of a specific skill gap."""
    skill: str = Field(..., description="The missing or missing-level skill")
    importance: str = Field(..., description="high, medium, or low based on job requirements")
    current_level: str = Field(..., description="none, basic, intermediate, advanced")
    recommendation: str = Field(..., description="Actionable advice to bridge the gap")


class MatchAnalysis(BaseModel):
    """Overall fit analysis between resume and job."""
    match_score: float = Field(..., ge=0, le=100, description="Overall match percentage (0-100)")
    matching_skills: List[str] = Field(default_factory=list, description="Skills the candidate has")
    missing_skills: List[SkillGap] = Field(default_factory=list, description="Critical skills missing")
    weak_skills: List[SkillGap] = Field(default_factory=list, description="Skills present but at lower level than required")
    overall_assessment: str = Field(..., description="Summary of the candidate's fit")


JSON_SCHEMA = """{
  "match_score": 75.5,
  "matching_skills": ["array of strings"],
  "missing_skills": [
    {
      "skill": "string",
      "importance": "high|medium|low",
      "current_level": "none",
      "recommendation": "string"
    }
  ],
  "weak_skills": [
    {
      "skill": "string",
      "importance": "high|medium|low",
      "current_level": "basic|intermediate",
      "recommendation": "string"
    }
  ],
  "overall_assessment": "string"
}"""


SYSTEM_PROMPT = f"""You are an expert career coach and hiring manager. Your job is to perform a detailed skill gap analysis between a candidate's resume and a job description.

Instructions:
1. Compare the Resume Skills/Experience against the Job Requirements.
2. Calculate a realistic Match Score (0-100) based on how well the candidate fits REQUIRED skills.
3. Identify Matching Skills (skills in both).
4. Identify Missing Skills (required skills not in resume).
5. Identify Weak Skills (skills present but experience seems too low for the role).
6. Provide actionable recommendations for filling gaps.

IMPORTANT: Be honest and critical. Don't hallucinate skills.

You MUST respond with ONLY valid JSON. Use this structure:
{JSON_SCHEMA}
"""


skill_gap_agent = Agent(
    get_llm_model(),
    output_type=str,
    retries=AGENT_RETRIES,
    system_prompt=SYSTEM_PROMPT,
)


def _extract_json_from_response(response: str) -> dict:
    """Helper to extract JSON from LLM response."""
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
    
    # Fallback
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {response[:500]}")
        raise ValueError(f"Could not extract valid JSON: {e}")


async def analyze_skill_gap(resume_data: ParsedResumeData, job_data: ParsedJobData) -> MatchAnalysis:
    """
    Analyze the gap between resume and job description.
    
    Args:
        resume_data: Parsed resume structure
        job_data: Parsed job structure
        
    Returns:
        MatchAnalysis: Detailed gap analysis
    """
    logger.info("Performing skill gap analysis")
    
    # Format inputs for the prompt
    resume_summary = {
        "skills": resume_data.skills,
        "experience": [f"{e.title} at {e.company} ({e.duration})" for e in resume_data.experience],
        "education": [f"{e.degree} in {e.field}" for e in resume_data.education]
    }
    
    job_summary = {
        "title": job_data.title,
        "required_skills": [f"{s.skill} ({s.importance})" for s in job_data.required_skills],
        "experience_required": job_data.required_experience_years
    }
    
    prompt = f"""Compare this RESUME against this JOB DESCRIPTION:

RESUME:
{json.dumps(resume_summary, indent=2)}

JOB DESCRIPTION:
{json.dumps(job_summary, indent=2)}

Analyze the fit and provide the output as valid JSON.
"""

    try:
        result = await skill_gap_agent.run(prompt)
        
        json_data = _extract_json_from_response(result.output)
        analysis = MatchAnalysis.model_validate(json_data)
        
        logger.info(f"Analysis complete. Match score: {analysis.match_score}")
        return analysis
        
    except Exception as e:
        logger.error(f"Failed to analyze skill gap: {e}")
        raise
