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
) -> dict[str, list[str] | int | float]:
    """
    Compare resume skills with job description skills using set operations.

    The matcher is intentionally rule-based for now. It treats two skills as a
    match only when their extracted names are exactly the same after basic
    whitespace cleanup. This makes the function deterministic, fast, easy to
    test, and simple to replace later with semantic AI matching.

    Args:
        resume_skills: Skills extracted from the candidate's resume.
        job_skills: Skills extracted from the job description.

    Returns:
        A dictionary containing the original normalized skill lists, matching
        details, counts, and a match percentage based on job requirements.
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
        match_percentage = 0.0
    else:
        # Score the resume by the percentage of job-required skills it covers.
        match_percentage = round(
            (matched_count / total_job_skills) * 100,
            2,
        )

    # Return sorted lists so API responses and tests stay deterministic.
    return {
        "resume_skills": sorted(resume_skill_set),
        "job_skills": sorted(job_skill_set),
        "matched_skills": sorted(matched_skill_set),
        "missing_skills": sorted(missing_skill_set),
        "extra_skills": sorted(extra_skill_set),
        "total_resume_skills": total_resume_skills,
        "total_job_skills": total_job_skills,
        "matched_count": matched_count,
        "match_percentage": match_percentage,
    }
