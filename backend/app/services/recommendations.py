"""
Generates grounded, explainable resume-improvement recommendations.

Every recommendation is derived directly from extracted resume/job data (never
invented), and pairs a concrete suggestion with a short "why" explaining how
it affects the candidate's score. This keeps the feedback specific and
actionable instead of generic ("improve your resume") advice.
"""

from app.services.extractor import has_measurable_achievements

MAX_PRIORITY_SKILLS = 6

CERTIFICATION_SIGNAL_WORDS = ("certified", "certification", "certificate", "license")

CATEGORY_LABELS = {
    "skills": "Skills",
    "experience": "Experience",
    "education": "Education",
    "projects": "Projects",
    "semantic_similarity": "Semantic Similarity",
}


def _insight(category: str, severity: str, message: str, why: str) -> dict[str, str]:
    return {"category": category, "severity": severity, "message": message, "why": why}


def _skills_insights(
    missing_required_skills: list[str],
    missing_preferred_skills: list[str],
    skills_score: float,
) -> list[dict[str, str]]:
    insights = []

    if missing_required_skills:
        shown = missing_required_skills[:MAX_PRIORITY_SKILLS]
        insights.append(
            _insight(
                "skills",
                "high",
                "Add evidence of these required skills (if you genuinely have them): "
                + ", ".join(shown) + ".",
                f"These terms appear in the job's required qualifications but not in your "
                f"resume, which is capping your Skills score at {skills_score}%.",
            )
        )

    if missing_preferred_skills:
        shown = missing_preferred_skills[:MAX_PRIORITY_SKILLS]
        insights.append(
            _insight(
                "skills",
                "medium",
                "Consider highlighting these nice-to-have skills: " + ", ".join(shown) + ".",
                "They're listed as preferred (not required), so they carry less weight, "
                "but including them helps you stand out among similarly-qualified candidates.",
            )
        )

    if not missing_required_skills and not missing_preferred_skills:
        insights.append(
            _insight(
                "skills",
                "low",
                "Your detected skills already cover the job's requirements well.",
                "No required or preferred skills from the job description were missing "
                "from your resume.",
            )
        )

    return insights


def _experience_insights(
    experience_entries: list[dict],
    experience_score: float,
) -> list[dict[str, str]]:
    insights = []

    if not experience_entries:
        insights.append(
            _insight(
                "experience",
                "high",
                "Add a Work Experience section with role, company, dates, and impact bullets.",
                "No experience entries were detected, so the matcher cannot verify "
                "role-relevant background, which caps your Experience score.",
            )
        )
        return insights

    all_bullets = [
        line for entry in experience_entries for line in (entry.get("description") or [])
    ]

    if all_bullets and not has_measurable_achievements(all_bullets):
        insights.append(
            _insight(
                "experience",
                "high",
                "Add measurable results to your experience bullets (%, counts, time saved, revenue, etc.).",
                "None of your experience bullets contain a number or metric. Quantified "
                "impact is one of the strongest signals recruiters and ATS scoring use "
                "to judge seniority and outcomes.",
            )
        )
    elif experience_score < 60:
        insights.append(
            _insight(
                "experience",
                "medium",
                "Mirror the job's core responsibilities more directly in your experience bullets.",
                f"Your Experience score ({experience_score}%) suggests your work history reads "
                "as only loosely related to this role's responsibilities.",
            )
        )

    return insights


def _education_insights(education_entries: list[dict], education_score: float) -> list[dict[str, str]]:
    if not education_entries and education_score < 70:
        return [
            _insight(
                "education",
                "medium",
                "Add an Education section with your degree, institution, and graduation year.",
                "The job description references a degree requirement, but no education "
                "entry was detected on your resume.",
            )
        ]
    return []


def _project_insights(project_entries: list[dict], projects_score: float) -> list[dict[str, str]]:
    insights = []

    if not project_entries:
        insights.append(
            _insight(
                "projects",
                "medium",
                "Add 2-3 projects that demonstrate the job's required skills in practice.",
                "No Projects section was detected. Projects are strong evidence of applied "
                "skill, especially when your work experience doesn't cover every requirement.",
            )
        )
        return insights

    weak_projects = [
        entry.get("name", "a project")
        for entry in project_entries
        if not entry.get("description")
    ]

    if weak_projects:
        insights.append(
            _insight(
                "projects",
                "medium",
                "Add 1-2 bullet points to these projects describing what you built and its impact: "
                + ", ".join(weak_projects[:3]) + ".",
                "Project entries with no description bullets give the matcher (and a "
                "recruiter) nothing to evaluate beyond the title.",
            )
        )
    elif projects_score < 55:
        insights.append(
            _insight(
                "projects",
                "low",
                "Tie your project descriptions more closely to this job's tech stack and goals.",
                f"Your Projects score ({projects_score}%) is low relative to this job, "
                "meaning the projects read as tangential to what this role needs.",
            )
        )

    return insights


def _certification_insights(
    certifications: list[str], job_text: str
) -> list[dict[str, str]]:
    job_text_lower = job_text.lower()
    job_mentions_certifications = any(word in job_text_lower for word in CERTIFICATION_SIGNAL_WORDS)

    if job_mentions_certifications and not certifications:
        return [
            _insight(
                "certifications",
                "medium",
                "Add relevant certifications if you hold any (the job description calls them out).",
                "The job description references certifications/licensing, but none were "
                "found on your resume.",
            )
        ]

    return []


def _formatting_insights(
    contact: dict[str, str | None],
    resume_word_count: int,
    has_any_section: bool,
) -> list[dict[str, str]]:
    insights = []

    if not contact.get("email") or not contact.get("phone"):
        insights.append(
            _insight(
                "formatting",
                "high",
                "Make sure your email and phone number are both clearly visible near the top of the resume.",
                "Missing contact details prevent recruiters (and applicant tracking systems) "
                "from reaching you even after a strong match.",
            )
        )

    if not contact.get("github") and not contact.get("linkedin"):
        insights.append(
            _insight(
                "formatting",
                "low",
                "Add a LinkedIn and/or GitHub link to your header.",
                "Technical roles are commonly cross-referenced against GitHub/LinkedIn; "
                "omitting them is a missed opportunity to reinforce your fit.",
            )
        )

    if not has_any_section:
        insights.append(
            _insight(
                "formatting",
                "high",
                "Use clear section headings (Education, Experience, Projects, Skills, Certifications).",
                "No standard section headings were detected, which makes both ATS parsing "
                "and this matcher's extraction far less reliable.",
            )
        )

    if resume_word_count < 150:
        insights.append(
            _insight(
                "formatting",
                "medium",
                "Expand your resume with more detail on responsibilities, projects, and outcomes.",
                f"At roughly {resume_word_count} words, your resume is likely too sparse for "
                "the matcher (and a recruiter) to assess fit confidently.",
            )
        )
    elif resume_word_count > 1200:
        insights.append(
            _insight(
                "formatting",
                "low",
                "Trim your resume to the most relevant, recent, and impactful content.",
                f"At roughly {resume_word_count} words, your resume may be longer than the "
                "1-2 pages recruiters typically spend under a minute scanning.",
            )
        )

    return insights


def _severity_rank(insight: dict[str, str]) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(insight["severity"], 3)


def build_resume_recommendations(
    missing_required_skills: list[str],
    missing_preferred_skills: list[str],
    matched_skills: list[str],
    extra_skills: list[str],
    category_scores: dict[str, float | None],
    overall_score: float,
    education_entries: list[dict],
    experience_entries: list[dict],
    project_entries: list[dict],
    certifications: list[str],
    contact: dict[str, str | None],
    resume_text: str,
    job_text: str,
) -> dict[str, object]:
    """Build a full set of grounded, explained recommendations for a resume/job pair."""
    insights: list[dict[str, str]] = []

    insights += _skills_insights(
        missing_required_skills, missing_preferred_skills, category_scores.get("skills") or 0.0
    )
    insights += _experience_insights(experience_entries, category_scores.get("experience") or 0.0)
    insights += _education_insights(education_entries, category_scores.get("education") or 0.0)
    insights += _project_insights(project_entries, category_scores.get("projects") or 0.0)
    insights += _certification_insights(certifications, job_text)
    insights += _formatting_insights(
        contact=contact,
        resume_word_count=len(resume_text.split()),
        has_any_section=bool(education_entries or experience_entries or project_entries),
    )

    insights.sort(key=_severity_rank)

    priority_skills = missing_required_skills[:MAX_PRIORITY_SKILLS] or missing_preferred_skills[:MAX_PRIORITY_SKILLS]
    suggested_resume_bullets = [
        f"Add a project or work bullet showing how you used {skill}, and quantify the result "
        f"(e.g. performance, time saved, users impacted)."
        for skill in priority_skills[:3]
    ]

    if overall_score >= 80:
        summary = "Strong fit. Focus on polish, measurable impact, and keeping key skills visible near the top."
    elif overall_score >= 60:
        summary = "Moderate fit. Add proof for missing skills and make relevant experience easier to spot."
    else:
        summary = "Needs improvement. Focus first on missing core skills and role-specific experience."

    return {
        "summary": summary,
        "priority_skills_to_add": priority_skills,
        "insights": insights,
        "suggested_resume_bullets": suggested_resume_bullets,
    }
