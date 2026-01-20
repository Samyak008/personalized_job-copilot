# ApplyWise - AI Job Application Copilot

> A production-grade agentic AI system built with Pydantic AI to supercharge your job search journey

**ApplyWise** transforms job applications from tedious manual work into an intelligent, data-driven process. Upload your resume, paste a job description, and receive a comprehensive analysis with personalized outreach content—all powered by a sophisticated multi-agent AI pipeline.

**Live Application**: [https://personalized-job-copilot.vercel.app/](https://personalized-job-copilot.vercel.app/)

**Demo Video**: [Watch 1-Minute Loom Video](https://drive.google.com/file/d/1JqCCXQ_aVrTNxIVJMJimA2EFnI8NbMY-/view)

---

## Key Features

### Multi-Agent AI Pipeline
Five specialized Pydantic AI agents work in harmony to deliver comprehensive analysis:

1. **Resume Parser Agent** - Extracts structured data from PDF resumes (skills, experience, education, projects, certifications)
2. **Job Analyzer Agent** - Parses job descriptions into structured requirements with skill importance classification
3. **Skill Gap Agent** - Performs intelligent matching with a 0-100 fit score and identifies missing/weak skills
4. **Strategy Planner Agent** - Creates actionable improvement plans with resume tweaks and learning paths
5. **Content Generator Agent** - Writes "Founder Mode" cold emails and LinkedIn DMs that get responses

### Actionable Insights
- **Match Score**: Data-driven 0-100 compatibility rating
- **Gap Analysis**: Detailed breakdown of missing and weak skills with recommendations
- **Resume Optimization**: Specific bullet points to add or modify
- **Interview Prep**: Potential questions and focus areas
- **Portfolio Ideas**: Project suggestions to demonstrate required skills

### "Founder Mode" Outreach
Generate high-signal, concise outreach messages that:
- Lead with **value** and **metrics**, not generic fluff
- Use **data from your resume** to establish credibility
- Keep it **under 75 words** for LinkedIn DMs
- Follow proven templates that get replies from busy hiring managers

### Production-Ready Engineering
- Async/await architecture with concurrent agent execution
- Structured error handling with graceful degradation
- Request correlation IDs for distributed tracing
- Retry logic with exponential backoff
- Comprehensive logging with Loguru
- Type-safe schemas with Pydantic validation

---

## Architecture

### Tech Stack

#### Frontend
| Technology | Purpose |
|------------|---------|
| **Next.js 16** | React framework with App Router |
| **TypeScript** | Type-safe development |
| **Tailwind CSS** | Utility-first styling |
| **shadcn/ui** | High-quality UI components |
| **TanStack Query** | Server state management |
| **Axios** | HTTP client |
| **Vercel** | Deployment platform |

#### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async API framework |
| **Pydantic AI** | Agent orchestration and validation |
| **Python 3.12** | Modern Python with type hints |
| **OpenRouter** | Multi-LLM gateway (Claude/GPT-4) |
| **Supabase** | PostgreSQL database + Auth |
| **SQLAlchemy** | Async ORM with migrations |
| **Docker** | Containerization |
| **Render/Railway** | Backend deployment |
| **uv** | Fast Python package manager |

### Agent Pipeline Flow

```mermaid
graph TD
    A[User Uploads Resume PDF] --> B[Resume Parser Agent]
    C[User Pastes Job Description] --> D[Job Analyzer Agent]
    
    B --> E[Skill Gap Agent]
    D --> E
    
    E --> F[Strategy Planner Agent]
    F --> G[Content Generator Agent]
    
    E --> H[Match Score & Gap Analysis]
    F --> I[Improvement Strategy]
    G --> J[Cold Email & LinkedIn DM]
    
    H --> K[Stored in Supabase]
    I --> K
    J --> K
    
    K --> L[User Dashboard]
    
    style B fill:#FF6F00
    style D fill:#FF6F00
    style E fill:#FF6F00
    style F fill:#FF6F00
    style G fill:#FF6F00
    style K fill:#4285F4
```

### System Design Highlights

- **Parallel Execution**: Resume and job analysis run concurrently to minimize latency
- **Graceful Degradation**: Pipeline returns partial results if strategy/content generation fails
- **Schema Validation**: All agent outputs validated with Pydantic before storage
- **Manual JSON Parsing**: Compatible with free-tier LLMs that may add markdown formatting
- **Correlation IDs**: Full request tracing from frontend to backend to agents to database

---

## Getting Started

### Prerequisites

- **Node.js** 18+ and **npm**
- **Python** 3.11+ (recommended: 3.12)
- **uv** package manager ([install](https://github.com/astral-sh/uv))
- **Docker** (optional, for containerized deployment)
- **Supabase** account (free tier)
- **OpenRouter** API key (free tier available)

### Backend Setup

```bash
cd backend

# Install dependencies with uv
uv sync

# Create environment file
cp .env.example .env
```

**Edit `.env` with your credentials:**

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.[project].supabase.co:5432/postgres

# LLM Provider (OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Security
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
ALLOWED_ORIGINS=https://personalized-job-copilot.vercel.app

# Logging
LOG_LEVEL=INFO
```

**Run database migrations:**

```bash
# Initialize Alembic (if first time)
uv run alembic upgrade head
```

**Start the development server:**

```bash
uv run uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local
```

**Edit `.env.local`:**

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_APP_ENV=production
```

**Start the Next.js dev server:**

```bash
npm run dev
```

---

## Docker Deployment

### Build and Run with Docker

```bash
# Backend
cd backend
docker build -t applywise-backend .
docker run -p 8000:8000 --env-file .env applywise-backend

# Frontend (production build)
cd frontend
npm run build
npm start
```

### Docker Compose (Full Stack)

```bash
# Coming soon: docker-compose.yml for one-command deployment
docker-compose up
```

---

## API Endpoints

### Health Check
```http
GET /health
```

### Create Analysis
```http
POST /api/v1/analyses/
Content-Type: multipart/form-data

resume_file: <PDF file>
job_description: <string>
```

**Response:**
```json
{
  "id": "uuid",
  "match_score": 78.5,
  "matching_skills": ["Python", "FastAPI", "React"],
  "missing_skills": [
    {
      "skill": "Docker",
      "importance": "high",
      "recommendation": "Build containerized applications..."
    }
  ],
  "strategy": {
    "resume_improvements": ["Add metrics to FastAPI project"],
    "skill_development_plan": [...],
    "project_ideas": [...]
  },
  "content": {
    "cold_email": "...",
    "linkedin_dm": "...",
    "interview_questions": [...]
  }
}
```

### Get Analysis by ID
```http
GET /api/v1/analyses/{analysis_id}
```

Full API documentation available at `/api/docs` when running the backend.

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_agents.py

# Run with verbose output
uv run pytest -v
```

### Frontend Tests

```bash
cd frontend

# Unit tests with Vitest
npm test

# E2E tests with Playwright
npx playwright test

# Run tests in watch mode
npm test -- --watch
```

---

## Design Principles

### Code Quality
- **DRY**: Reusable agent base classes and utility functions
- **SOLID**: Single-responsibility agents with clear interfaces
- **Type Safety**: Full TypeScript + Python type hints
- **Error Handling**: Structured errors with correlation IDs

### Agent Design
- **Schema-First**: Pydantic models define all agent I/O
- **Retry Logic**: Configurable retries with exponential backoff
- **Logging**: Comprehensive instrumentation with Loguru
- **Manual JSON Parsing**: Handles markdown-wrapped JSON from free-tier LLMs

### UX Polish
- **Loading States**: Real-time agent progress visualization
- **Error States**: Clear, actionable error messages
- **Responsive Design**: Mobile-first with Tailwind CSS
- **Accessibility**: WCAG 2.1 AA compliance with shadcn/ui

---

## Deployment

### Frontend (Vercel)

1. Push code to GitHub
2. Connect repository to Vercel
3. Configure environment variables in Vercel dashboard
4. Deploy automatically on push to `main`

**Live URL**: [https://personalized-job-copilot.vercel.app/](https://personalized-job-copilot.vercel.app/)

### Backend (Render/Railway)
Render is deployed using Dockerfile.
To keep the render from sleeping, CI pipeline is set to ping the app every 10 minutes.

### Environment Variables

Set these in your deployment platform:

**Frontend:**
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Backend:**
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `DATABASE_URL`
- `OPENROUTER_API_KEY`
- `SECRET_KEY`
- `ALLOWED_ORIGINS`

---

## Demo Video

**[Watch the demo video](https://drive.google.com/file/d/1JqCCXQ_aVrTNxIVJMJimA2EFnI8NbMY-/view)**

**What's covered:**
- Live walkthrough of the application
- Agent pipeline in action
- Generated outreach content
- Technical architecture explanation

---

## Future Enhancements

- **Email Integration**: Send outreach directly from the app
- **Chrome Extension**: Apply from job boards with one click
- **Application Tracking**: Track sent applications and responses
- **Company Research**: Auto-fetch company data to personalize content
- **Interview Scheduling**: Integration with calendar APIs
- **Cover Letter Generation**: Full-length cover letter drafts
- **Batch Processing**: Analyze multiple jobs simultaneously
- **Vector Search**: Find similar jobs from your saved analyses


---

## Acknowledgments

- **Pydantic AI** for the robust agent framework
- **OpenRouter** for free-tier LLM access
- **Supabase** for PostgreSQL + Auth infrastructure
- **Vercel & Render** for generous free-tier hosting

---


*Supercharge your job search with intelligent AI agents*