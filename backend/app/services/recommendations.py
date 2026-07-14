MAX_PRIORITY_SKILLS = 5


def build_resume_recommendations(
    missing_skills: list[str],
    matched_skills: list[str],
    extra_skills: list[str],
    keyword_score: float,
    semantic_score: float | None,
    overall_score: float,
) -> dict[str, list[str] | str]:
    """
    Build practical resume-improvement recommendations from match results.

    These recommendations are intentionally grounded in the detected skills and
    scores so the API does not invent experience the candidate may not have.
    """
    priority_skills = missing_skills[:MAX_PRIORITY_SKILLS]
    actions = []
    resume_bullets = []

    if priority_skills:
        actions.append(
            "Add evidence for these job-required skills if you have real experience with them: "
            + ", ".join(priority_skills)
            + "."
        )

        for skill in priority_skills[:3]:
            resume_bullets.append(
                f"Add a project or work bullet showing how you used {skill} and what result it produced."
            )
    else:
        actions.append(
            "Your detected skills cover the job requirements well. Focus on making achievements measurable."
        )

    if keyword_score < 50:
        actions.append(
            "Increase keyword alignment by reflecting the job description's exact skill terms where they are truthful."
        )
    elif keyword_score < 75:
        actions.append(
            "You have a partial keyword match. Strengthen the skills section and project bullets around the missing requirements."
        )
    else:
        actions.append(
            "Keyword alignment is strong. Prioritize clearer impact, scope, and outcomes in your experience bullets."
        )

    if semantic_score is None:
        actions.append(
            "Semantic scoring was not available for this match, so recommendations are based on detected skills."
        )
    elif semantic_score < 60:
        actions.append(
            "The resume and job description read as only loosely related. Add role-specific projects, responsibilities, and outcomes."
        )
    elif semantic_score < 80:
        actions.append(
            "The resume is semantically related to the role. Improve fit by mirroring the job's responsibilities in your experience section."
        )
    else:
        actions.append(
            "The resume reads closely aligned with the role. Polish wording and quantify impact to improve recruiter confidence."
        )

    if matched_skills:
        actions.append(
            "Keep the strongest matched skills visible near the top: "
            + ", ".join(matched_skills[:5])
            + "."
        )

    if extra_skills and overall_score < 80:
        actions.append(
            "Move less relevant skills lower on the resume so the job-critical skills stand out first."
        )

    if overall_score >= 80:
        summary = "Strong fit. Your resume mainly needs polish and stronger proof of impact."
    elif overall_score >= 60:
        summary = "Moderate fit. Add proof for missing skills and make relevant experience easier to spot."
    else:
        summary = "Needs improvement. Focus first on missing core skills and role-specific experience."

    return {
        "summary": summary,
        "priority_skills_to_add": priority_skills,
        "actions": actions,
        "suggested_resume_bullets": resume_bullets,
    }
