from typing import Any


_latest_resume_analysis: dict[str, Any] | None = None


def save_latest_resume_analysis(
    filename: str,
    email: str | None,
    phone: str | None,
    skills: list[str],
    text: str,
) -> None:
    """
    Store the most recently uploaded resume analysis in memory.

    This is useful during the early API-building stage because it lets the
    matching endpoint reuse skills extracted from the last uploaded resume
    without requiring a database yet.
    """
    global _latest_resume_analysis

    _latest_resume_analysis = {
        "filename": filename,
        "email": email,
        "phone": phone,
        "skills": skills.copy(),
        "text": text,
    }


def get_latest_resume_analysis() -> dict[str, Any] | None:
    """
    Return a copy of the most recently uploaded resume analysis.

    Returns:
        The latest resume analysis if a resume has been uploaded during the
        current server session; otherwise, None.
    """
    if _latest_resume_analysis is None:
        return None

    latest_resume_analysis = _latest_resume_analysis.copy()
    latest_resume_analysis["skills"] = _latest_resume_analysis["skills"].copy()

    return latest_resume_analysis
