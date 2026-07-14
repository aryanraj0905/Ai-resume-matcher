from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.parser import PDFParsingError, extract_text_from_pdf
from app.services.extractor import (
    extract_certifications,
    extract_education,
    extract_email,
    extract_experience,
    extract_github,
    extract_linkedin,
    extract_phone,
    extract_projects,
    extract_skills,
)
from app.models.database import get_resume_analysis, save_resume_analysis

router = APIRouter()

UPLOAD_FOLDER = Path("uploads")
ALLOWED_FILE_EXTENSION = ".pdf"
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
}

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def _validate_pdf_upload(file: UploadFile) -> None:
    filename = file.filename or ""
    file_extension = Path(filename).suffix.lower()

    if file_extension != ALLOWED_FILE_EXTENSION:
        raise HTTPException(
            status_code=400,
            detail="Only PDF resume uploads are supported.",
        )

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Uploaded resume must be a PDF file.",
        )


def _build_safe_upload_path(original_filename: str) -> Path:
    safe_stem = Path(original_filename).stem.strip().replace(" ", "_")
    safe_stem = "".join(
        character for character in safe_stem if character.isalnum() or character in ("-", "_")
    )

    if not safe_stem:
        safe_stem = "resume"

    safe_filename = f"{safe_stem}_{uuid4().hex}.pdf"
    return UPLOAD_FOLDER / safe_filename


MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    _validate_pdf_upload(file)

    original_filename = file.filename or "resume.pdf"
    file_path = _build_safe_upload_path(original_filename)

    total_bytes_written = 0
    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            total_bytes_written += len(chunk)
            if total_bytes_written > MAX_UPLOAD_BYTES:
                buffer.close()
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=400,
                    detail="Resume file is too large. Maximum upload size is 10 MB.",
                )
            buffer.write(chunk)

    if total_bytes_written == 0:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        extracted_text = extract_text_from_pdf(str(file_path))
    except PDFParsingError as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    email = extract_email(extracted_text)
    phone = extract_phone(extracted_text)
    github = extract_github(extracted_text)
    linkedin = extract_linkedin(extracted_text)
    skills = extract_skills(extracted_text)
    education = extract_education(extracted_text)
    certifications = extract_certifications(extracted_text)
    experience = extract_experience(extracted_text)
    projects = extract_projects(extracted_text)

    resume_id = save_resume_analysis(
        filename=original_filename,
        stored_filename=file_path.name,
        email=email,
        phone=phone,
        github=github,
        linkedin=linkedin,
        skills=skills,
        education=education,
        certifications=certifications,
        experience=experience,
        projects=projects,
        text=extracted_text,
    )

    return {
        "message": "Resume uploaded successfully!",
        "resume_id": resume_id,
        "filename": original_filename,
        "stored_filename": file_path.name,
        "email": email,
        "phone": phone,
        "github": github,
        "linkedin": linkedin,
        "skills": skills,
        "education": education,
        "certifications": certifications,
        "experience": experience,
        "projects": projects,
        "text": extracted_text,
    }


@router.get("/{resume_id}")
def get_resume(resume_id: int):
    resume_analysis = get_resume_analysis(resume_id)

    if resume_analysis is None:
        raise HTTPException(
            status_code=404,
            detail=f"Resume with id {resume_id} was not found.",
        )

    return resume_analysis
