# ApplyWise — AI Job Application Copilot

ApplyWise is a full-stack generative AI agent application that helps users analyze job descriptions against their resumes, identify skill gaps, generate personalized outreach, and prepare for interviews.

The system is designed as a **production-grade agentic workflow** using **Pydantic AI** with strict schema validation, retries, and clean API boundaries.

---

## 1. Problem Statement

Job seekers spend significant time manually:
- Evaluating whether they are a good fit for a role
- Understanding missing skills
- Writing personalized cold emails and LinkedIn DMs
- Preparing for interviews

This process is repetitive, error-prone, and difficult to scale.

ApplyWise automates this entire workflow using structured AI agents while maintaining high reliability and strong user experience.

---

## 2. Core User Flow

1. User uploads their resume (PDF)
2. User pastes a job description or job URL
3. User clicks **Analyze**
4. System returns:
   - Resume ↔ Job match score
   - Missing and weak skills
   - Resume improvement suggestions
   - Personalized cold email
   - Personalized LinkedIn DM
   - Interview preparation questions
5. Results can be saved and revisited

---

## 3. System Architecture

### Frontend
- Next.js (App Router)
- Tailwind CSS
- shadcn/ui components
- Hosted on Vercel

### Backend
- FastAPI
- Pydantic AI for agent orchestration
- OpenRouter LLM provider (free tier model)
- SQLite or Postgres for persistence
- Hosted on Render or Railway

---

## 4. Agent Design (Pydantic AI)

The backend uses a **multi-agent pipeline**, not a single prompt-based system.

### Agent Pipeline

```text
Resume Parser
   ↓
Job Description Analyzer Agent
   ↓
Resume Match & Skill Gap Agent
   ↓
Strategy Planner Agent
   ↓
Content Generator Agent
   ↓
Pydantic Validation Layer
