"""
Strategy Planner Agent

Generates actionable improvement strategies based on skill gap analysis.
"""

import json
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import List
from loguru import logger

from app.agents.base import get_llm_model, AGENT_RETRIES
from app.agents.skill_gap import MatchAnalysis
from app.agents.job_analyzer import ParsedJobData
from app.utils import extract_json_from_response


class ImprovementAction(BaseModel):
    """Specific actionable step to improve."""
    action: str = Field(..., description="What to do (e.g., 'Build a project using FastAPI')")
    priority: str = Field(..., description="immediate, short-term, or long-term")
    estimated_time: str = Field(..., description="Time to complete (e.g., '2 weeks')")
    resource_type: str = Field(..., description="course, project, article, practice")


class ImprovementStrategy(BaseModel):
    """Comprehensive strategy for landing the job."""
    resume_improvements: List[str] = Field(..., description="Specific bullet points to add/modify")
    skill_development_plan: List[ImprovementAction] = Field(..., description="Plan to close skill gaps")
    interview_focus_areas: List[str] = Field(..., description="Technical topics to prepare for")
    project_ideas: List[str] = Field(..., description="Portfolio projects to demonstrate missing skills")


JSON_SCHEMA = """{
  "resume_improvements": ["array of strings"],
  "skill_development_plan": [
    {
      "action": "string",
      "priority": "immediate|short-term|long-term",
      "estimated_time": "string",
      "resource_type": "string"
    }
  ],
  "interview_focus_areas": ["array of strings"],
  "project_ideas": ["array of strings"]
}"""


SYSTEM_PROMPT = f"""You are an expert career strategist. Your goal is to create a concrete, actionable plan for a candidate to land a specific job.

Instructions:
1. Analyze the Match Score and Skill Gaps.
2. Suggest specific Resume Tweaks to better highlight existing matching skills.
3. Create a Skill Development Plan for missing/weak skills.
4. Suggest Interview Topics based on the job requirements.
5. Propose Project Ideas that would demonstrate the required skills.

IMPORTANT: Be specific. Don't just say "Learn Python", say "Build a REST API with Python".

You MUST respond with ONLY valid JSON. Use this structure:
{JSON_SCHEMA}
"""


strategy_agent = Agent(
    get_llm_model(),
    output_type=str,
    retries=AGENT_RETRIES,
    system_prompt=SYSTEM_PROMPT,
)


async def plan_strategy(
    match_analysis: MatchAnalysis, 
    job_data: ParsedJobData
) -> ImprovementStrategy:
    """
    Generate an improvement strategy.
    
    Args:
        match_analysis: The output from the skill gap agent
        job_data: The parsed job description
        
    Returns:
        ImprovementStrategy: Actionable plan
    """
    logger.info("Generating improvement strategy")
    
    # Prepare input summary
    analysis_summary = {
        "match_score": match_analysis.match_score,
        "missing_skills": [s.skill for s in match_analysis.missing_skills],
        "overall_assessment": match_analysis.overall_assessment
    }
    
    job_summary = {
        "title": job_data.title,
        "required_skills": [s.skill for s in job_data.required_skills]
    }
    
    prompt = f"""Create a strategy for this candidate:

ANALYSIS:
{json.dumps(analysis_summary, indent=2)}

TARGET JOB:
{json.dumps(job_summary, indent=2)}

Provide the strategy as valid JSON.
"""

    try:
        result = await strategy_agent.run(prompt)
        
        json_data = extract_json_from_response(result.output)
        strategy = ImprovementStrategy.model_validate(json_data)
        
        logger.info(f"Strategy generated with {len(strategy.skill_development_plan)} actions")
        return strategy
        
    except Exception as e:
        logger.error(f"Failed to generate strategy: {e}")
        raise
