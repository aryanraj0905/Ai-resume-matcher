from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from app.services.extractor import extract_skills
from app.services.matcher import match_resume_to_job
from app.models.database import get_latest_resume_analysis, get_resume_analysis

router = APIRouter()

MIN_JOB_DESCRIPTION_LENGTH = 20


class JobDescription(BaseModel):
    description: str

    @field_validator("description")
    @classmethod
    def description_must_be_substantial(cls, value: str) -> str:
        if len(value.strip()) < MIN_JOB_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Job description must be at least {MIN_JOB_DESCRIPTION_LENGTH} characters."
            )
        return value


class JobMatchRequest(BaseModel):
    description: str
    resume_id: int | None = None
    resume_skills: list[str] | None = None
    resume_text: str | None = None

    @field_validator("description")
    @classmethod
    def description_must_be_substantial(cls, value: str) -> str:
        if len(value.strip()) < MIN_JOB_DESCRIPTION_LENGTH:
            raise ValueError(
                f"Job description must be at least {MIN_JOB_DESCRIPTION_LENGTH} characters."
            )
        return value


@router.post("/analyze")
def analyze_job(job: JobDescription):
    skills = extract_skills(job.description)

    return {
        "message": "Job description analyzed successfully!",
        "skills": skills
    }


@router.post("/match")
def match_resume_with_job(job: JobMatchRequest):
    resume_profile: dict | None = None

    if job.resume_id is not None:
        resume_profile = get_resume_analysis(job.resume_id)
        if resume_profile is None:
            raise HTTPException(
                status_code=400,
                detail=f"Resume with id {job.resume_id} was not found.",
            )
    elif job.resume_skills is not None:
        resume_profile = {
            "skills": job.resume_skills,
            "text": job.resume_text or "",
            "education": [],
            "certifications": [],
            "experience": [],
            "projects": [],
            "email": None,
            "phone": None,
            "github": None,
            "linkedin": None,
        }
    else:
        resume_profile = get_latest_resume_analysis()
        if resume_profile is None:
            raise HTTPException(
                status_code=400,
                detail="Upload a resume first or provide resume_skills.",
            )

    match_result = match_resume_to_job(
        resume_profile=resume_profile,
        job_description=job.description,
    )

    return {
        "message": "Resume matched with job description successfully!",
        **match_result,
    }
