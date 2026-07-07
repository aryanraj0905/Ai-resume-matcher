from fastapi import FastAPI

from app.routes.resume import router as resume_router
from app.routes.job import router as job_router

app = FastAPI(
    title="AI Resume Intelligence Platform",
    description="An AI-powered Resume Analysis and Job Matching API",
    version="1.0.0"
)

# Resume Routes
app.include_router(
    resume_router,
    prefix="/resume",
    tags=["Resume"]
)

# Job Routes
app.include_router(
    job_router,
    prefix="/job",
    tags=["Job"]
)


@app.get("/")
def home():
    return {
        "message": "Welcome to the AI Resume Intelligence Platform!"
    }


@app.get("/health")
def health():
    return {
        "status": "Server is running"
    }