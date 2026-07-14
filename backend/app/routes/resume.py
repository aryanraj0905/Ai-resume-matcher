from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
import shutil

from app.services.parser import PDFParsingError, extract_text_from_pdf
from app.services.extractor import (
    extract_email,
    extract_phone,
    extract_skills,
)
from app.models.database import save_resume_analysis

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


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    _validate_pdf_upload(file)

    original_filename = file.filename or "resume.pdf"
    file_path = _build_safe_upload_path(original_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text_from_pdf(str(file_path))
    except PDFParsingError as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    email = extract_email(extracted_text)
    phone = extract_phone(extracted_text)
    skills = extract_skills(extracted_text)

    resume_id = save_resume_analysis(
        filename=original_filename,
        stored_filename=file_path.name,
        email=email,
        phone=phone,
        skills=skills,
        text=extracted_text,
    )

    return {
        "message": "Resume uploaded successfully!",
        "resume_id": resume_id,
        "filename": original_filename,
        "stored_filename": file_path.name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "text": extracted_text
    }
