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


def test_job_analyze_rejects_too_short_description():
    response = client.post("/job/analyze", json={"description": "short"})

    assert response.status_code == 422


def test_job_match_uses_provided_resume_skills(monkeypatch):
    monkeypatch.setattr(
        "app.services.matcher._semantic_similarity_or_none", lambda *a, **k: None
    )

    response = client.post(
        "/job/match",
        json={
            "description": "Looking for Python, FastAPI, SQL, and Docker experience.",
            "resume_skills": ["Python", "SQL"],
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert set(result["matched_skills"]) == {"Python", "SQL"}
    assert "Docker" in result["missing_skills"]
    assert "FastAPI" in result["missing_skills"]
    assert set(result["category_scores"].keys()) == {
        "skills", "experience", "education", "projects", "semantic_similarity",
    }
    assert result["recommendations"]["summary"]


def test_job_match_rejects_too_short_description():
    response = client.post(
        "/job/match",
        json={"description": "short", "resume_skills": ["Python"]},
    )

    assert response.status_code == 422


def test_job_match_rejects_missing_resume_context(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")

    response = client.post(
        "/job/match",
        json={"description": "Looking for Python and SQL experience."},
    )

    assert response.status_code == 400
    assert "Upload a resume first" in response.json()["detail"]


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


def test_resume_upload_rejects_empty_file(tmp_path, monkeypatch):
    monkeypatch.setattr(resume, "UPLOAD_FOLDER", tmp_path)

    response = client.post(
        "/resume/upload",
        files={"file": ("resume.pdf", b"", "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty."


def test_resume_upload_accepts_valid_pdf_with_extracted_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(resume, "UPLOAD_FOLDER", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")

    resume_text = (
        "Aryan\naryan@example.com\ngithub.com/aryan\n\n"
        "SKILLS\nPython FastAPI SQL"
    )

    response = client.post(
        "/resume/upload",
        files={
            "file": (
                "../Aryan Resume.pdf",
                _create_pdf_bytes(resume_text),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["filename"] == "../Aryan Resume.pdf"
    assert isinstance(result["resume_id"], int)
    assert result["email"] == "aryan@example.com"
    assert result["github"] == "https://github.com/aryan"
    assert result["skills"] == ["FastAPI", "Python", "SQL"]
    assert result["stored_filename"].startswith("Aryan_Resume_")
    assert result["stored_filename"].endswith(".pdf")
    assert (tmp_path / result["stored_filename"]).exists()
    assert result["education"] == []
    assert result["certifications"] == []


def test_get_resume_returns_persisted_analysis(tmp_path, monkeypatch):
    monkeypatch.setattr(resume, "UPLOAD_FOLDER", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")

    upload_response = client.post(
        "/resume/upload",
        files={
            "file": (
                "resume.pdf",
                _create_pdf_bytes("Aryan\naryan@example.com\nPython FastAPI"),
                "application/pdf",
            )
        },
    )
    resume_id = upload_response.json()["resume_id"]

    response = client.get(f"/resume/{resume_id}")

    assert response.status_code == 200
    assert response.json()["id"] == resume_id


def test_get_resume_rejects_unknown_id(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")

    response = client.get("/resume/999")

    assert response.status_code == 404


def test_job_match_uses_persisted_resume_id(tmp_path, monkeypatch):
    monkeypatch.setattr(resume, "UPLOAD_FOLDER", tmp_path)
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")
    monkeypatch.setattr(
        "app.services.matcher._semantic_similarity_or_none", lambda *a, **k: 70.0
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
            "description": "Looking for Python, FastAPI, SQL, and Docker experience.",
            "resume_id": resume_id,
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert set(result["matched_skills"]) == {"FastAPI", "Python", "SQL"}
    assert result["missing_skills"] == ["Docker"]
    assert result["category_scores"]["semantic_similarity"] == 70.0


def test_job_match_rejects_unknown_resume_id(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")

    response = client.post(
        "/job/match",
        json={
            "description": "Looking for Python experience on this team.",
            "resume_id": 999,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Resume with id 999 was not found."
