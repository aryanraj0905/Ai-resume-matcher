# ResumeMatch AI

An AI-powered resume matcher that scores how well a resume fits a job description — using real semantic similarity (Sentence Transformers), not keyword counting — and returns category-level scores plus explained, actionable recommendations.

## Overview

Upload a resume (PDF) and paste a job description. ResumeMatch AI parses the resume into structured data (contact info, skills, education, experience, projects, certifications), extracts what the job actually requires (required vs. preferred skills, responsibilities), and produces:

- An **overall compatibility score** (0-100%)
- **Category scores**: Skills, Experience, Education, Projects, and Semantic Similarity
- **Matched / missing / extra skills**, split into required vs. preferred
- **AI recommendations** — each with a plain-English reason tied to your actual score, not generic advice

## Features

- **Semantic matching** via `sentence-transformers` (`all-MiniLM-L6-v2`), comparing resume content against the job's actual responsibilities/requirements rather than the whole posting verbatim (avoids diluting the signal with boilerplate).
- **Weighted category scoring** — Skills (35%), Experience (25%), Projects (15%), Education (10%), Semantic Similarity (15%). If semantic scoring is unavailable, weight is redistributed proportionally across the remaining categories rather than silently zeroing the score.
- **Robust resume extraction**: email, phone, GitHub/LinkedIn URLs, skills, education (degree/institution/year), certifications, work experience (title/duration/bullets), and projects (name/description/tech stack) — parsed with section-header heuristics rather than a fixed template.
- **Grounded AI recommendations**: every suggestion is derived from the actual extracted data (missing required/preferred skills, unquantified experience bullets, thin project descriptions, missing certifications the job calls out, missing contact info, resume length) — nothing is invented.
- **Production-minded API**: input validation (short/empty job descriptions, non-PDF uploads, oversized files, encrypted/corrupt PDFs), friendly error messages, CORS configuration via environment variables.
- **Modern SaaS-style dashboard**: circular score ring, category breakdown bars + chart, skill badges, and an AI insights feed — fully responsive.

## Architecture

```
                    ┌─────────────────────┐
                    │   React Frontend     │
                    │ (Vite + Tailwind)    │
                    └──────────┬──────────┘
                               │ REST (axios)
                    ┌──────────▼──────────┐
                    │   FastAPI Backend    │
                    │ ┌──────────────────┐ │
                    │ │ routes/          │ │  resume upload, job match
                    │ ├──────────────────┤ │
                    │ │ services/        │ │  extraction, section parsing,
                    │ │  extractor.py    │ │  matcher.py, recommendations.py
                    │ │  matcher.py      │ │
                    │ │  recommendations │ │
                    │ ├──────────────────┤ │
                    │ │ ai/              │ │  embeddings, cosine similarity,
                    │ │  embeddings.py   │ │  category scoring
                    │ │  similarity.py   │ │
                    │ │  category_scoring│ │
                    │ ├──────────────────┤ │
                    │ │ models/          │ │  SQLite persistence
                    │ │  database.py     │ │
                    │ └──────────────────┘ │
                    └──────────────────────┘
```

**Request flow:** upload resume → parse PDF text (PyMuPDF) → extract structured fields → persist to SQLite → submit a job description → extract required/preferred skills + core responsibilities → score each category (keyword overlap + sentence-embedding cosine similarity) → combine into a weighted overall score → generate recommendations from the same extracted data.

## Tech Stack

**Backend:** FastAPI, Sentence Transformers (`all-MiniLM-L6-v2`), PyMuPDF, SQLite, pytest
**Frontend:** React 19, Vite, Tailwind CSS v4, React Router, Axios, Recharts, lucide-react

## Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/Scripts/activate      # Windows (Git Bash): source venv/Scripts/activate
                                   # macOS/Linux:        source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env               # adjust as needed
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000` (interactive docs at `/docs`). The embedding model downloads automatically on first use and is cached for subsequent runs.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env               # set VITE_API_BASE_URL if not using the default
npm run dev
```

The app runs at `http://localhost:5173`.

### Running tests

```bash
cd backend
pytest
```

## API Endpoints

| Method | Endpoint         | Description                                                              |
|--------|------------------|---------------------------------------------------------------------------|
| GET    | `/health`        | Health check                                                              |
| POST   | `/resume/upload` | Upload a PDF resume (multipart `file`); returns parsed structured data    |
| GET    | `/resume/{id}`   | Fetch a previously parsed resume by ID                                    |
| POST   | `/job/analyze`   | Extract skills from a job description                                    |
| POST   | `/job/match`     | Match a resume (`resume_id`, or `resume_skills`/`resume_text`) against a job `description`; returns category scores, overall score, and recommendations |

See `/docs` for full request/response schemas once the backend is running.

## Screenshots

> _Add screenshots here: landing page, upload flow, and the results dashboard._

- `docs/screenshots/landing.png`
- `docs/screenshots/upload.png`
- `docs/screenshots/results.png`

## Deployment

### Backend (Render)

A `render.yaml` is included. Connect the repo in Render, set the root directory to `backend/`, and set `CORS_ALLOWED_ORIGINS` to your deployed frontend URL (comma-separated if there's more than one, e.g. a Vercel preview + production URL).

Two things worth knowing about the free plan:

- **Cold starts.** The free instance spins down after inactivity. The first request after a spin-down needs to boot the process and load the embedding model, which the frontend's "warming up" timeout message is written to cover — but it can still take 30-60s. Upgrading to a paid instance (or pinging `/health` on a schedule) avoids this.
- **Ephemeral disk.** Without an attached Render disk, the SQLite DB and uploaded PDFs reset on every deploy/restart — see the comment in `render.yaml` for how to attach one if you need resume lookups to survive restarts.

### Frontend (Vercel)

Import the repo in Vercel with the root directory set to `frontend/` (Vite is auto-detected). Set the `VITE_API_BASE_URL` environment variable to your deployed backend URL. `vercel.json` rewrites all routes to `index.html` so client-side routing works on refresh/deep links.

## Future Improvements

- Support DOCX resume uploads (currently PDF-only)
- Multi-resume comparison against a single job description
- Persist match history per resume and visualize score trends over time
- Fine-tune or swap the embedding model for a resume/job-specific domain
- Authenticated accounts for saving resumes and job matches across sessions
