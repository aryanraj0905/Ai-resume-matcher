from fastapi import FastAPI
from app.routes.resume import router as resume_router

app = FastAPI(
    title="AI Resume Matcher",
    description="An AI-powered Resume Matching API",
    version="1.0.0"
)

app.include_router(
    resume_router,
    prefix="/resume",
    tags=["Resume"]
)


@app.get("/")
def home():
    return {
        "message": "Welcome to the AI Resume Matcher API!"
    }


@app.get("/health")
def health():
    return {
        "status": "Server is running"
    }