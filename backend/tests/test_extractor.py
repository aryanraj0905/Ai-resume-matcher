from app.services.extractor import (
    extract_certifications,
    extract_education,
    extract_experience,
    extract_github,
    extract_linkedin,
    extract_projects,
    extract_required_and_preferred_skills,
    extract_skills,
    extract_years_of_experience,
)

SAMPLE_RESUME = """Jane Doe
jane@example.com
github.com/janedoe
linkedin.com/in/janedoe

EDUCATION
Bachelor of Technology in Computer Science, ABC University, 2023

EXPERIENCE
Software Engineer, TechCorp
Jan 2023 - Present
Built REST APIs using Python and FastAPI serving 10000 requests per day
Reduced latency by 30 percent through caching

PROJECTS
Resume Matcher
Built an AI powered resume matcher using Python and FastAPI
Achieved 95 percent accuracy on test data

SKILLS
Python, FastAPI, SQL, Docker

CERTIFICATIONS
AWS Certified Solutions Architect
"""


def test_extract_github_normalizes_url():
    assert extract_github(SAMPLE_RESUME) == "https://github.com/janedoe"


def test_extract_linkedin_normalizes_url():
    assert extract_linkedin(SAMPLE_RESUME) == "https://linkedin.com/in/janedoe"


def test_extract_github_returns_none_when_absent():
    assert extract_github("No profile links here.") is None


def test_extract_skills_ignores_profile_urls():
    skills = extract_skills(SAMPLE_RESUME)
    assert "GitHub" not in skills
    assert "Python" in skills
    assert "FastAPI" in skills


def test_extract_education_finds_degree_and_year():
    entries = extract_education(SAMPLE_RESUME)
    assert len(entries) == 1
    assert "Bachelor" in entries[0]["degree"]
    assert entries[0]["year"] == "2023"


def test_extract_certifications_returns_list_of_entries():
    certifications = extract_certifications(SAMPLE_RESUME)
    assert certifications == ["AWS Certified Solutions Architect"]


def test_extract_experience_groups_title_duration_and_bullets():
    entries = extract_experience(SAMPLE_RESUME)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["title"] == "Software Engineer, TechCorp"
    assert entry["duration"] == "Jan 2023 - Present"
    assert len(entry["description"]) == 2


def test_extract_projects_groups_name_bullets_and_technologies():
    entries = extract_projects(SAMPLE_RESUME)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["name"] == "Resume Matcher"
    assert "Python" in entry["technologies"]
    assert "FastAPI" in entry["technologies"]
    assert len(entry["description"]) == 2


def test_extract_years_of_experience_from_text():
    assert extract_years_of_experience("We require 3+ years of experience.") == 3.0
    assert extract_years_of_experience("No years mentioned here.") is None


def test_extract_required_and_preferred_skills_splits_sections():
    job_description = """
    Requirements:
    - Python and FastAPI experience required

    Preferred Qualifications:
    - AWS and Docker experience is a bonus
    """
    required, preferred = extract_required_and_preferred_skills(job_description)
    assert "Python" in required
    assert "FastAPI" in required
    assert "AWS" in preferred
    assert "Docker" in preferred
    assert "AWS" not in required


def test_extract_required_and_preferred_skills_falls_back_to_whole_text():
    required, preferred = extract_required_and_preferred_skills(
        "Looking for someone with Python and SQL skills."
    )
    assert set(required) == {"Python", "SQL"}
    assert preferred == []
