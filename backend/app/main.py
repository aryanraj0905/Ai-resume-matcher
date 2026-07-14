import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import CORS_ALLOWED_ORIGINS
from app.routes.resume import router as resume_router
from app.routes.job import router as job_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI Resume Intelligence Platform",
    description="An AI-powered Resume Analysis and Job Matching API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return friendly, human-readable messages instead of raw pydantic errors."""
    first_error = exc.errors()[0] if exc.errors() else None
    message = first_error["msg"] if first_error else "Invalid request."

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": message},
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
