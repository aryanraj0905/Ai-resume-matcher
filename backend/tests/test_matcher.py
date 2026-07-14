from app.services.matcher import match_resume_to_job

JOB_DESCRIPTION = """
Requirements:
- Strong Python and FastAPI skills
- Experience with SQL and Docker
- Bachelor degree in Computer Science

Preferred Qualifications:
- AWS experience
- Kubernetes knowledge

Responsibilities:
- Build and maintain REST APIs
"""


def _base_resume_profile(**overrides) -> dict:
    profile = {
        "skills": ["Python", "FastAPI", "SQL"],
        "text": "Experienced backend engineer skilled in Python and FastAPI.",
        "education": [{"degree": "Bachelor of Technology", "institution": "ABC", "year": "2022", "raw_text": "Bachelor of Technology, ABC, 2022"}],
        "experience": [{"title": "Backend Engineer", "duration": "2022 - Present", "description": ["Built REST APIs with Python and FastAPI."]}],
        "projects": [{"name": "API Service", "description": ["Built a REST API using FastAPI."], "technologies": ["FastAPI", "Python"]}],
        "certifications": [],
        "email": "test@example.com",
        "phone": "+919876543210",
        "github": None,
        "linkedin": None,
    }
    profile.update(overrides)
    return profile


def test_match_resume_to_job_returns_all_expected_keys(monkeypatch):
    monkeypatch.setattr(
        "app.services.matcher._semantic_similarity_or_none", lambda *a, **k: 75.0
    )

    result = match_resume_to_job(_base_resume_profile(), JOB_DESCRIPTION)

    assert set(result["category_scores"].keys()) == {
        "skills", "experience", "education", "projects", "semantic_similarity",
    }
    assert 0 <= result["overall_score"] <= 100
    assert "Python" in result["matched_skills"]
    assert "Docker" in result["missing_required_skills"]
    assert "Kubernetes" in result["missing_preferred_skills"]
    assert "recommendations" in result
    assert "insights" in result["recommendations"]


def test_missing_required_skills_lower_skills_score(monkeypatch):
    monkeypatch.setattr(
        "app.services.matcher._semantic_similarity_or_none", lambda *a, **k: 50.0
    )

    strong = match_resume_to_job(_base_resume_profile(), JOB_DESCRIPTION)
    weak = match_resume_to_job(
        _base_resume_profile(skills=["Python"]), JOB_DESCRIPTION
    )

    assert weak["category_scores"]["skills"] < strong["category_scores"]["skills"]
    assert weak["overall_score"] < strong["overall_score"]


def test_overall_score_is_deterministic_not_random(monkeypatch):
    monkeypatch.setattr(
        "app.services.matcher._semantic_similarity_or_none", lambda *a, **k: 60.0
    )

    first = match_resume_to_job(_base_resume_profile(), JOB_DESCRIPTION)
    second = match_resume_to_job(_base_resume_profile(), JOB_DESCRIPTION)

    assert first["overall_score"] == second["overall_score"]
    assert first["category_scores"] == second["category_scores"]


def test_semantic_similarity_none_redistributes_weight(monkeypatch):
    monkeypatch.setattr(
        "app.services.matcher._semantic_similarity_or_none", lambda *a, **k: None
    )

    result = match_resume_to_job(_base_resume_profile(), JOB_DESCRIPTION)

    assert result["category_scores"]["semantic_similarity"] is None
    assert 0 <= result["overall_score"] <= 100


def test_empty_resume_profile_scores_low(monkeypatch):
    monkeypatch.setattr(
        "app.services.matcher._semantic_similarity_or_none", lambda *a, **k: 10.0
    )

    empty_profile = _base_resume_profile(
        skills=[], education=[], experience=[], projects=[], certifications=[]
    )
    result = match_resume_to_job(empty_profile, JOB_DESCRIPTION)

    assert result["category_scores"]["skills"] == 0.0
    assert result["overall_score"] < 40
