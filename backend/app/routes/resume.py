from fastapi import APIRouter, UploadFile, File
import os
import shutil

from app.services.parser import extract_text_from_pdf
from app.services.extractor import (
    extract_email,
    extract_phone,
    extract_skills,
)
from app.utils.helpers import save_latest_resume_analysis

router = APIRouter()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    # Save uploaded PDF
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(file_path)

    # Extract information
    email = extract_email(extracted_text)
    phone = extract_phone(extracted_text)
    skills = extract_skills(extracted_text)

    save_latest_resume_analysis(
        filename=file.filename,
        email=email,
        phone=phone,
        skills=skills,
        text=extracted_text,
    )

    # Return response
    return {
        "message": "Resume uploaded successfully!",
        "filename": file.filename,
        "email": email,
        "phone": phone,
        "skills": skills,
        "text": extracted_text
    }
