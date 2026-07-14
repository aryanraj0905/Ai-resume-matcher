import logging

from app.ai.embeddings import EmbeddingModelUnavailable
from app.ai.similarity import calculate_semantic_similarity
from app.config import ENABLE_SEMANTIC_MATCHING
from app.services.recommendations import build_resume_recommendations

logger = logging.getLogger(__name__)

SEMANTIC_SCORE_WEIGHT = 0.65
KEYWORD_SCORE_WEIGHT = 0.35


def _normalize_skills(skills: list[str]) -> set[str]:
    """
    Normalize a list of skill names into a clean set of unique skills.

    This helper keeps the public matcher function focused on matching logic
    while centralizing small data-cleaning rules in one reusable place.

    Args:
        skills: A list of skill names extracted from a resume or job
            description.

    Returns:
        A set of unique, non-empty skill names with surrounding whitespace
        removed.
    """
    # Convert each skill to a stripped string so accidental spaces do not
    # create false mismatches such as "Python" vs " Python ".
    return {skill.strip() for skill in skills if skill and skill.strip()}


def match_skills(
    resume_skills: list[str],
    job_skills: list[str],
    resume_text: str | None = None,
    job_description: str | None = None,
) -> dict[str, list[str] | dict[str, list[str] | str] | int | float | None]:
    """
    Compare resume skills with job description skills and optional semantics.

    The keyword matcher remains deterministic and easy to inspect. When full
    resume text and job description text are provided, semantic similarity is
    layered on top using embeddings.

    Args:
        resume_skills: Skills extracted from the candidate's resume.
        job_skills: Skills extracted from the job description.
        resume_text: Full text extracted from the resume.
        job_description: Full job description text.

    Returns:
        A dictionary containing keyword matching details, semantic score, and
        an overall weighted score.
    """
    # Store skills in sets to remove duplicates and enable efficient matching.
    resume_skill_set = _normalize_skills(resume_skills)
    job_skill_set = _normalize_skills(job_skills)

    # Find skills that appear in both the resume and the job description.
    matched_skill_set = resume_skill_set.intersection(job_skill_set)

    # Find job-required skills that the resume does not currently contain.
    missing_skill_set = job_skill_set.difference(resume_skill_set)

    # Find resume skills that are not explicitly required by the job.
    extra_skill_set = resume_skill_set.difference(job_skill_set)

    # Count unique resume skills after normalization and duplicate removal.
    total_resume_skills = len(resume_skill_set)

    # Count unique job skills after normalization and duplicate removal.
    total_job_skills = len(job_skill_set)

    # Count how many job-required skills were found in the resume.
    matched_count = len(matched_skill_set)

    # Avoid division by zero when the job description has no detected skills.
    if total_job_skills == 0:
        keyword_score = 0.0
    else:
        # Score the resume by the percentage of job-required skills it covers.
        keyword_score = round(
            (matched_count / total_job_skills) * 100,
            2,
        )

    semantic_score = None

    if resume_text and job_description and ENABLE_SEMANTIC_MATCHING:
        logger.info("Calculating semantic resume match score.")
        try:
            semantic_score = calculate_semantic_similarity(
                resume_text=resume_text,
                job_description=job_description,
            )
        except EmbeddingModelUnavailable as exc:
            logger.warning("Skipping semantic score: %s", exc)

    if semantic_score is None:
        overall_score = keyword_score
    else:
        overall_score = round(
            (semantic_score * SEMANTIC_SCORE_WEIGHT)
            + (keyword_score * KEYWORD_SCORE_WEIGHT),
            2,
        )

    matched_skills = sorted(matched_skill_set)
    missing_skills = sorted(missing_skill_set)
    extra_skills = sorted(extra_skill_set)
    recommendations = build_resume_recommendations(
        missing_skills=missing_skills,
        matched_skills=matched_skills,
        extra_skills=extra_skills,
        keyword_score=keyword_score,
        semantic_score=semantic_score,
        overall_score=overall_score,
    )

    # Return sorted lists so API responses and tests stay deterministic.
    return {
        "resume_skills": sorted(resume_skill_set),
        "job_skills": sorted(job_skill_set),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "total_resume_skills": total_resume_skills,
        "total_job_skills": total_job_skills,
        "matched_count": matched_count,
        "match_percentage": keyword_score,
        "keyword_score": keyword_score,
        "semantic_score": semantic_score,
        "overall_score": overall_score,
        "recommendations": recommendations,
    }
