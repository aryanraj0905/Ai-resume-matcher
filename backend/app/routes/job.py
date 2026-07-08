from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.extractor import extract_skills
from app.services.matcher import match_skills
from app.utils.helpers import get_latest_resume_analysis

router = APIRouter()


class JobDescription(BaseModel):
    description: str


class JobMatchRequest(BaseModel):
    description: str
    resume_skills: list[str] | None = None
    resume_text: str | None = None


@router.post("/analyze")
def analyze_job(job: JobDescription):
    skills = extract_skills(job.description)

    return {
        "message": "Job description analyzed successfully!",
        "skills": skills
    }


@router.post("/match")
def match_resume_with_job(job: JobMatchRequest):
    resume_skills = job.resume_skills
    resume_text = job.resume_text

    if resume_skills is None:
        latest_resume_analysis = get_latest_resume_analysis()

        if latest_resume_analysis is None:
            raise HTTPException(
                status_code=400,
                detail="Upload a resume first or provide resume_skills.",
            )

        resume_skills = latest_resume_analysis["skills"]
        resume_text = latest_resume_analysis["text"]

    job_skills = extract_skills(job.description)
    match_result = match_skills(
        resume_skills=resume_skills,
        job_skills=job_skills,
        resume_text=resume_text,
        job_description=job.description,
    )

    return {
        "message": "Resume matched with job description successfully!",
        **match_result
    }
