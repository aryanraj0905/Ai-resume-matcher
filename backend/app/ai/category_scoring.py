"""
Category-level scoring for resume-to-job matching.

Instead of a single opaque match percentage, the matcher scores five
independent categories (skills, experience, education, projects, and overall
semantic similarity) and then combines them with fixed, explainable weights.
This mirrors how a human recruiter actually evaluates a resume: skills and
experience matter most, projects and education provide supporting signal.
"""

import logging

from app.ai.embeddings import EmbeddingModelUnavailable
from app.ai.similarity import calculate_text_similarity
from app.services.extractor import DEGREE_PATTERN

logger = logging.getLogger(__name__)

CATEGORY_WEIGHTS = {
    "skills": 0.35,
    "experience": 0.25,
    "projects": 0.15,
    "education": 0.10,
    "semantic_similarity": 0.15,
}


def _safe_similarity(text_a: str, text_b: str) -> float | None:
    if not text_a.strip() or not text_b.strip():
        return None

    try:
        return calculate_text_similarity(text_a, text_b)
    except EmbeddingModelUnavailable as exc:
        logger.warning("Semantic scoring unavailable: %s", exc)
        return None


def score_skills(
    resume_skills: set[str],
    required_skills: set[str],
    preferred_skills: set[str],
) -> float:
    """Score skill coverage, weighting required skills far above preferred ones."""
    if not required_skills and not preferred_skills:
        return 100.0 if resume_skills else 0.0

    required_ratio = (
        len(resume_skills & required_skills) / len(required_skills)
        if required_skills
        else 1.0
    )
    preferred_ratio = (
        len(resume_skills & preferred_skills) / len(preferred_skills)
        if preferred_skills
        else 1.0
    )

    if required_skills and preferred_skills:
        score = (required_ratio * 0.8) + (preferred_ratio * 0.2)
    elif required_skills:
        score = required_ratio
    else:
        score = preferred_ratio

    return round(score * 100, 2)


def score_experience(
    experience_entries: list[dict],
    resume_years: float | None,
    job_required_years: float | None,
    resume_text: str,
    job_text: str,
) -> float:
    """Score experience relevance using semantic fit plus years-of-experience fit."""
    experience_text = "\n".join(
        f"{entry.get('title', '')} {' '.join(entry.get('description') or [])}"
        for entry in experience_entries
    ).strip()

    semantic_score = _safe_similarity(experience_text or resume_text, job_text)

    if semantic_score is None:
        # No embedding model available: fall back to a coarse presence check.
        semantic_score = 60.0 if experience_entries else 20.0

    if job_required_years is None or resume_years is None:
        return round(semantic_score, 2)

    years_ratio = min(resume_years / job_required_years, 1.2) if job_required_years > 0 else 1.0
    years_score = min(years_ratio, 1.0) * 100

    return round((semantic_score * 0.6) + (years_score * 0.4), 2)


def score_education(education_entries: list[dict], job_text: str) -> float:
    """Score education fit, treating a degree requirement as the key signal."""
    job_requires_degree = bool(DEGREE_PATTERN.search(job_text)) or "degree" in job_text.lower()

    if not job_requires_degree:
        return 100.0 if education_entries else 70.0

    if not education_entries:
        return 30.0

    education_text = "\n".join(
        entry.get("raw_text") or entry.get("degree") or "" for entry in education_entries
    )
    semantic_score = _safe_similarity(education_text, job_text)

    if semantic_score is None:
        return 65.0

    return round(max(50.0, semantic_score), 2)


def score_projects(
    project_entries: list[dict],
    required_skills: set[str],
    preferred_skills: set[str],
    job_text: str,
) -> float:
    """Score projects using both tech-stack overlap and semantic relevance."""
    if not project_entries:
        return 35.0

    project_text = "\n".join(
        f"{entry.get('name', '')} {' '.join(entry.get('description') or [])}"
        for entry in project_entries
    ).strip()

    project_technologies: set[str] = set()
    for entry in project_entries:
        project_technologies.update(entry.get("technologies") or [])

    job_skills = required_skills | preferred_skills
    skill_overlap_ratio = (
        len(project_technologies & job_skills) / len(job_skills) if job_skills else 0.5
    )

    semantic_score = _safe_similarity(project_text, job_text)
    if semantic_score is None:
        return round(skill_overlap_ratio * 100, 2)

    return round((skill_overlap_ratio * 100 * 0.5) + (semantic_score * 0.5), 2)


def combine_category_scores(category_scores: dict[str, float | None]) -> float:
    """
    Combine category scores into one overall score using fixed weights.

    Any category that could not be scored (e.g. semantic similarity when the
    embedding model is unavailable) has its weight redistributed proportionally
    across the remaining categories so the total always sums to 100%.
    """
    available = {
        name: score for name, score in category_scores.items() if score is not None
    }

    if not available:
        return 0.0

    available_weight_total = sum(CATEGORY_WEIGHTS[name] for name in available)
    weighted_sum = sum(
        score * (CATEGORY_WEIGHTS[name] / available_weight_total)
        for name, score in available.items()
    )

    return round(weighted_sum, 2)
