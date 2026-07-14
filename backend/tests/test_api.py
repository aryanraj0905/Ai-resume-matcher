import fitz
import pytest
from fastapi.testclient import TestClient

from app.ai.similarity import cosine_similarity
from app.main import app
from app.models import database
from app.routes import resume


client = TestClient(app)


def _create_pdf_bytes(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def test_health_endpoint_returns_running_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "Server is running"}


def test_job_analyze_extracts_skills():
    response = client.post(
        "/job/analyze",
        json={"description": "We need Python, FastAPI, and SQL experience."},
    )

    assert response.status_code == 200
    assert response.json()["skills"] == ["FastAPI", "Python", "SQL"]


def test_job_match_uses_provided_resume_skills():
    response = client.post(
        "/job/match",
        json={
            "description": "Looking for Python, FastAPI, SQL, and Docker.",
            "resume_skills": ["Python", "SQL"],
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["matched_skills"] == ["Python", "SQL"]
    assert result["missing_skills"] == ["Docker", "FastAPI"]
    assert result["match_percentage"] == 50.0
    assert result["keyword_score"] == 50.0
    assert result["semantic_score"] is None
    assert result["overall_score"] == 50.0


def test_job_match_combines_keyword_and_semantic_scores(monkeypatch):
    monkeypatch.setattr("app.services.matcher.ENABLE_SEMANTIC_MATCHING", True)
    monkeypatch.setattr(
        "app.services.matcher.calculate_semantic_similarity",
        lambda resume_text, job_description: 80.0,
    )

    response = client.post(
        "/job/match",
        json={
            "description": "Looking for Python, FastAPI, SQL, and Docker.",
            "resume_skills": ["Python", "SQL"],
            "resume_text": "Built backend APIs using Python and SQL.",
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["keyword_score"] == 50.0
    assert result["semantic_score"] == 80.0
    assert result["overall_score"] == 69.5


def test_cosine_similarity_scores_identical_vectors_as_one():
    assert cosine_similarity(
        [1.0, 2.0, 3.0],
        [1.0, 2.0, 3.0],
    ) == pytest.approx(1.0)


def test_resume_upload_rejects_non_pdf():
    response = client.post(
        "/resume/upload",
        files={
            "file": (
                "resume.docx",
                b"not a pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF resume uploads are supported."


def test_resume_upload_rejects_invalid_pdf(tmp_path, monkeypatch):
    monkeypatch.setattr(resume, "UPLOAD_FOLDER", tmp_path)

    response = client.post(
        "/resume/upload",
        files={"file": ("resume.pdf", b"not a valid pdf", "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or unreadable PDF file."
    assert list(tmp_path.iterdir()) == []


def test_resume_upload_accepts_valid_pdf_with_safe_stored_filename(tmp_path, monkeypatch):
    monkeypatch.setattr(resume, "UPLOAD_FOLDER", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")

    response = client.post(
        "/resume/upload",
        files={
            "file": (
                "../Aryan Resume.pdf",
                _create_pdf_bytes("Aryan\naryan@example.com\nPython FastAPI SQL"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["filename"] == "../Aryan Resume.pdf"
    assert isinstance(result["resume_id"], int)
    assert result["email"] == "aryan@example.com"
    assert result["skills"] == ["FastAPI", "Python", "SQL"]
    assert result["stored_filename"].startswith("Aryan_Resume_")
    assert result["stored_filename"].endswith(".pdf")
    assert (tmp_path / result["stored_filename"]).exists()


def test_job_match_uses_persisted_resume_id(tmp_path, monkeypatch):
    monkeypatch.setattr(resume, "UPLOAD_FOLDER", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")
    monkeypatch.setattr("app.services.matcher.ENABLE_SEMANTIC_MATCHING", True)
    monkeypatch.setattr(
        "app.services.matcher.calculate_semantic_similarity",
        lambda resume_text, job_description: 70.0,
    )

    upload_response = client.post(
        "/resume/upload",
        files={
            "file": (
                "resume.pdf",
                _create_pdf_bytes("Aryan\naryan@example.com\nPython FastAPI SQL"),
                "application/pdf",
            )
        },
    )
    resume_id = upload_response.json()["resume_id"]

    response = client.post(
        "/job/match",
        json={
            "description": "Looking for Python, FastAPI, SQL, and Docker.",
            "resume_id": resume_id,
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["matched_skills"] == ["FastAPI", "Python", "SQL"]
    assert result["missing_skills"] == ["Docker"]
    assert result["keyword_score"] == 75.0
    assert result["semantic_score"] == 70.0
    assert result["overall_score"] == 71.75


def test_job_match_rejects_unknown_resume_id(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")

    response = client.post(
        "/job/match",
        json={
            "description": "Looking for Python.",
            "resume_id": 999,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Resume with id 999 was not found."
