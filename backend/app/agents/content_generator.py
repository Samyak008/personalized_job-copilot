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



SYSTEM_PROMPT = f"""You are an expert ghostwriter creating high-signal "Founder Mode" outreach messages.
Your goal is to write cold emails and LinkedIn DMs that get replies from busy founders and hiring managers.

### 🚫 STRICT PROHIBITIONS (Instant Fail if used):
- NEVER start with "Hi, I'm [Name]" or "I am writing to apply".
- NEVER use generic fluff like "I believe my skills are a good fit" or "I am passionate about".
- NEVER use words like "thrilled", "excited", "keen", "opportunity", "honing".
- NEVER sound like a desperate job seeker. Sound like a peer offering value.

### ✅ "FOUNDER MODE" FORMULA:
1. **The Hook**: Immediately state a relevant achievement or specific observation about their company/tech.
2. **The Value**: Quantitative proof you've done this before (metrics, numbers, specific tech).
3. **The Ask**: Low friction (e.g., "Worth a chat?", "Open to a 10min demo?").

### TONE:
- Concise (under 75 words for DMs).
- Direct, confident, professional.
- Data-driven (use numbers from the resume).

### TEMPLATES TO MIMIC (Adapt these):

**LinkedIn Connection Note (No subject):**
"Hey [Name], saw you're building [Product/Feature].
I just built a similar [Tech Stack] pipeline handling 10k reqs/day, cutting costs 75%.
Would love to compare notes on [Specific Tech Challenge].
[Resume Link if space]"

**Cold Email:**
"Subject: [Specific Problem] at [Company] / [My Name]

[Name],

Saw [Company] is scaling its [Tech Team/Product].

I recently engineered an automated AI pipeline using [Tech Stack] that reduced delivery time by 85% (6h → 45m) for [Previous Company].
I suspect [Company] faces similar scaling challenges with [Specific Tech].

Built this specifically for the role: [GitHub Link/Portfolio]

Worth a brief chat this week?

[My Name]
[Resume Link]"

**Context:**
You will be given:
1. Candidate's Resume (Parsed Data)
2. Job Description (Parsed Data)
3. Skill Gap Analysis
4. Strategic Angle

**Task:**
Generate the `cold_email` and `linkedin_dm` following the rules above.

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
