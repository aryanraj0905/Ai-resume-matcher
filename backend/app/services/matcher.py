import logging

from app.ai.category_scoring import (
    CATEGORY_WEIGHTS,
    combine_category_scores,
    score_education,
    score_experience,
    score_projects,
    score_skills,
)
from app.ai.embeddings import EmbeddingModelUnavailable
from app.ai.similarity import calculate_semantic_similarity
from app.config import ENABLE_SEMANTIC_MATCHING
from app.services.extractor import (
    build_job_core_text,
    extract_required_and_preferred_skills,
    extract_years_of_experience,
)
from app.services.recommendations import build_resume_recommendations

logger = logging.getLogger(__name__)


def _normalize_skills(skills: list[str]) -> set[str]:
    """Normalize a list of skill names into a clean set of unique skills."""
    return {skill.strip() for skill in skills if skill and skill.strip()}


def _semantic_similarity_or_none(resume_text: str, job_description: str) -> float | None:
    if not ENABLE_SEMANTIC_MATCHING or not resume_text or not job_description:
        return None

    try:
        return calculate_semantic_similarity(
            resume_text=resume_text, job_description=job_description
        )
    except EmbeddingModelUnavailable as exc:
        logger.warning("Skipping semantic score: %s", exc)
        return None


def match_resume_to_job(resume_profile: dict, job_description: str) -> dict:
    """
    Compare a fully-parsed resume profile against a job description.

    Produces per-category scores (skills, experience, education, projects,
    semantic similarity), a weighted overall score, and grounded AI
    recommendations explaining how to improve the match.

    Args:
        resume_profile: Parsed resume data as stored by the resume upload
            endpoint (skills, education, experience, projects,
            certifications, contact info, and full text).
        job_description: Full job posting text provided by the user.

    Returns:
        A dictionary with skill match details, category scores, the overall
        score, and recommendations.
    """
    resume_skill_set = _normalize_skills(resume_profile.get("skills") or [])

    required_skills, preferred_skills = extract_required_and_preferred_skills(job_description)
    required_skill_set = _normalize_skills(required_skills)
    preferred_skill_set = _normalize_skills(preferred_skills)
    job_skill_set = required_skill_set | preferred_skill_set

    matched_skill_set = resume_skill_set & job_skill_set
    missing_required_set = required_skill_set - resume_skill_set
    missing_preferred_set = preferred_skill_set - resume_skill_set
    extra_skill_set = resume_skill_set - job_skill_set

    resume_text = resume_profile.get("text") or ""
    education_entries = resume_profile.get("education") or []
    experience_entries = resume_profile.get("experience") or []
    project_entries = resume_profile.get("projects") or []
    certifications = resume_profile.get("certifications") or []

    resume_years = extract_years_of_experience(resume_text)
    job_required_years = extract_years_of_experience(job_description)
    job_core_text = build_job_core_text(job_description)

    category_scores = {
        "skills": score_skills(resume_skill_set, required_skill_set, preferred_skill_set),
        "experience": score_experience(
            experience_entries, resume_years, job_required_years, resume_text, job_core_text
        ),
        "education": score_education(education_entries, job_description),
        "projects": score_projects(
            project_entries, required_skill_set, preferred_skill_set, job_core_text
        ),
        "semantic_similarity": _semantic_similarity_or_none(resume_text, job_description),
    }

    overall_score = combine_category_scores(category_scores)

    contact = {
        "email": resume_profile.get("email"),
        "phone": resume_profile.get("phone"),
        "github": resume_profile.get("github"),
        "linkedin": resume_profile.get("linkedin"),
    }

    recommendations = build_resume_recommendations(
        missing_required_skills=sorted(missing_required_set),
        missing_preferred_skills=sorted(missing_preferred_set),
        matched_skills=sorted(matched_skill_set),
        extra_skills=sorted(extra_skill_set),
        category_scores=category_scores,
        overall_score=overall_score,
        education_entries=education_entries,
        experience_entries=experience_entries,
        project_entries=project_entries,
        certifications=certifications,
        contact=contact,
        resume_text=resume_text,
        job_text=job_description,
    )

    return {
        "resume_skills": sorted(resume_skill_set),
        "required_skills": sorted(required_skill_set),
        "preferred_skills": sorted(preferred_skill_set),
        "matched_skills": sorted(matched_skill_set),
        "missing_skills": sorted(missing_required_set | missing_preferred_set),
        "missing_required_skills": sorted(missing_required_set),
        "missing_preferred_skills": sorted(missing_preferred_set),
        "extra_skills": sorted(extra_skill_set),
        "total_resume_skills": len(resume_skill_set),
        "total_job_skills": len(job_skill_set),
        "matched_count": len(matched_skill_set),
        "category_scores": category_scores,
        "category_weights": CATEGORY_WEIGHTS,
        "overall_score": overall_score,
        "match_percentage": overall_score,
        "recommendations": recommendations,
    }
