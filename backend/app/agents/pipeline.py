"""
Pipeline Orchestrator

Orchestrates the flow of data between all agents:
Resume -> Job -> Skill Gap -> Strategy -> Content
"""

from dataclasses import dataclass
from loguru import logger
import asyncio

from app.agents.resume_parser import parse_resume, parse_resume_file, ParsedResumeData
from app.agents.job_analyzer import analyze_job_description, ParsedJobData
from app.agents.skill_gap import analyze_skill_gap, MatchAnalysis
from app.agents.strategy_planner import plan_strategy, ImprovementStrategy
from app.agents.content_generator import generate_content, GeneratedContent


@dataclass
class PipelineResult:
    """Aggregated result of the full analysis pipeline."""
    resume_data: ParsedResumeData
    job_data: ParsedJobData
    match_analysis: MatchAnalysis
    strategy: ImprovementStrategy
    content: GeneratedContent


async def run_analysis_pipeline(
    resume_text: str, 
    job_description: str
) -> PipelineResult:
    """
    Run the complete analysis pipeline with text inputs.
    
    Args:
        resume_text: Raw resume text
        job_description: Raw job description
        
    Returns:
        PipelineResult: Complete analysis artifact
    """
    logger.info("Starting analysis pipeline (Text Mode)")
    
    # Run Parse and Analyze in parallel (they don't depend on each other)
    logger.debug("Step 1: Parsing Resume and Job Description")
    resume_task = parse_resume(resume_text)
    job_task = analyze_job_description(job_description)
    
    resume_data, job_data = await asyncio.gather(resume_task, job_task)
    
    # Step 2: Skill Gap Analysis (Validation)
    logger.debug("Step 2: Analyzing Skill Gap")
    match_analysis = await analyze_skill_gap(resume_data, job_data)
    
    # Step 3: Strategy & Content (Parallel, dependent on Gap Analysis)
    logger.debug("Step 3: Generating Strategy and Content")
    strategy_task = plan_strategy(match_analysis, job_data)
    
    # Wait for strategy first? Or run content in parallel?
    # Content gen needs strategy for "focus_areas"
    strategy = await strategy_task
    
    content_task = generate_content(resume_data, job_data, strategy)
    content = await content_task
    
    logger.info(f"Pipeline complete. Match Score: {match_analysis.match_score}/100")
    
    return PipelineResult(
        resume_data=resume_data,
        job_data=job_data,
        match_analysis=match_analysis,
        strategy=strategy,
        content=content
    )


async def run_file_analysis_pipeline(
    file_content: bytes,
    filename: str,
    job_description: str
) -> PipelineResult:
    """
    Run the complete analysis pipeline with a file input.
    """
    logger.info(f"Starting analysis pipeline (File Mode: {filename})")
    
    # We can reuse the same logic, just starting with parse_resume_file
    logger.debug("Step 1: Parsing Resume File and Job Description")
    resume_task = parse_resume_file(file_content, filename)
    job_task = analyze_job_description(job_description)
    
    resume_data, job_data = await asyncio.gather(resume_task, job_task)
    
    # Continue with logic... (duplicated for clarity/flexibility)
    logger.debug("Step 2: Analyzing Skill Gap")
    match_analysis = await analyze_skill_gap(resume_data, job_data)
    
    logger.debug("Step 3: Generating Strategy")
    strategy = await plan_strategy(match_analysis, job_data)
    
    logger.debug("Step 4: Generating Content")
    content = await generate_content(resume_data, job_data, strategy)
    
    logger.info(f"Pipeline complete. Match Score: {match_analysis.match_score}/100")
    
    return PipelineResult(
        resume_data=resume_data,
        job_data=job_data,
        match_analysis=match_analysis,
        strategy=strategy,
        content=content
    )
