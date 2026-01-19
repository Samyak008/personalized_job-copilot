import asyncio
from app.agents.resume_parser import parse_resume
from app.agents.job_analyzer import analyze_job_description
from app.agents.skill_gap import analyze_skill_gap

# Sample Data
RESUME_TEXT = """
John Doe
Software Engineer
Email: john@example.com

SKILLS
Python, Django, PostgreSQL, Docker, Git, REST APIs

EXPERIENCE
Backend Developer at StartupInc (2020-Present)
- Built scalable backends using Django and Postgres
- Deployed on AWS using Docker
"""

JOB_DESC = """
Senior Python Developer
TechCorp - Remote

Requirements:
- 5+ years of experience with Python
- Strong knowledge of FastAPI or Flask (Django is a plus)
- Experience with AWS (Lambda, EC2) and Kubernetes
- Must have experience with microservices architecture
- Knowledge of GraphQL is preferred

Responsibilities:
- Design and implement microservices
- Mentor junior developers
"""


async def verify_phase_3b():
    print("--- 1. Parsing Resume ---")
    resume = await parse_resume(RESUME_TEXT)
    print(f"Resume parsed: {resume.name}, {len(resume.skills)} skills")
    
    print("\n--- 2. Analyzing Job ---")
    job = await analyze_job_description(JOB_DESC)
    print(f"Job Title: {job.title}")
    print(f"Company: {job.company}")
    print(f"Required Skills ({len(job.required_skills)}):")
    for s in job.required_skills:
        print(f"  - {s.skill} ({s.importance})")
        
    print("\n--- 3. Analyzing Skill Gap ---")
    gap = await analyze_skill_gap(resume, job)
    print(f"Match Score: {gap.match_score}/100")
    print(f"Assessment: {gap.overall_assessment}")
    
    print("\nMissing Skills:")
    for s in gap.missing_skills:
        print(f"  - {s.skill} (Importance: {s.importance}) -> Rec: {s.recommendation}")
        
    print("\n✅ Phase 3B Verification Complete!")


if __name__ == "__main__":
    asyncio.run(verify_phase_3b())
