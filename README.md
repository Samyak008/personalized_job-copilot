    # ApplyWise - AI Job Application Copilot

**ApplyWise** is an intelligent agentic workflow designed to supercharge your job search. It doesn't just "write cover letters"—it analyzes your resume against specific job descriptions, identifies skill gaps, formulates a personalized interview strategy, and generates high-impact, founder-mode outreach messages.

![CleanShot 2024-01-20 at 19 33 24](https://github.com/Samyak008/personalized_job-copilot/assets/placeholder-image.png)
*(Replace with actual screenshot)*

## Features

-   **Smart Resume Parsing**: Upload PDF resumes; extract skills, experience, and contact info automatically.
-   **Deep Job Analysis**: Matches your profile against job descriptions to find alignment and critical gaps.
-   **Agentic Workflow**: real-time multi-step process:
    1.  **Parser Agent**: Structures raw data.
    2.  **Analyst Agent**: Evaluates fit score and gaps.
    3.  **Strategy Agent**: Brainstorms interview prep & angle.
    4.  **Writer Agent**: Drafts highly personalized emails & DMs.
-   **"Founder Mode" Outreach**: Generates concise, high-signal messages optimized for LinkedIn and cold emails (no generic fluff).
-   **Live Progress UI**: Visualizes the AI agents working in real-time.

## Tech Stack

### Frontend
-   **Framework**: Next.js 15 (App Router)
-   **Language**: TypeScript
-   **Styling**: Tailwind CSS + Shadcn/UI
-   **State**: React Query (TanStack Query)
-   **Deployment**: Vercel

### Backend
-   **Framework**: FastAPI (Python 3.12)
-   **AI Framework**: PydanticAI + LangChain
-   **LLM**: OpenRouter (Claude 3.5 Sonnet / GPT-4o)
-   **Database**: Supabase (PostgreSQL + pgvector)
-   **Package Manager**: `uv` (Astral)
-   **Deployment**: Render (Dockerized)

## Local Development

### Prerequisites
-   Node.js 18+
-   Python 3.11+
-   Docker (optional, for container testing)
-   Supabase Project

### 1. Clone & Setup
```bash
git clone https://github.com/Samyak008/personalized-job-copilot.git
cd personalized-job-copilot
```

### 2. Backend Setup
```bash
cd backend
# create environment and install dependencies
uv sync

# Create .env file
cp .env.example .env
# Edit .env with your Supabase and OpenRouter keys

# Run development server
uv run uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local with Supabase keys and API URL (http://localhost:8000/api/v1)

# Run development server
npm run dev
```

Visit `http://localhost:3000` to start applying!

## Deployment

Detailed deployment instructions can be found in [DEPLOYMENT.md](./DEPLOYMENT.md).

-   **Frontend**: Deployed to Vercel.
-   **Backend**: Containerized with Docker and deployed to Render.

## Testing

Run the full test suite:

```bash
# Backend Tests
cd backend
uv run pytest

# Frontend Tests
cd frontend
npm test

# E2E Tests
npx playwright test
```

## License
MIT