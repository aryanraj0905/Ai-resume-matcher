import re
from app.data.skills import TECHNICAL_SKILLS


def extract_email(text: str):
    """
    Extract the first email address from the resume.
    """
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None


def extract_phone(text: str):
    """
    Extract an Indian phone number.
    """
    pattern = r"(?:\+91[- ]?)?[6-9]\d{9}"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return None


def extract_skills(text: str):
    """
    Extract technical skills from the resume.
    """
    normalized_text = text.lower()

    found_skills = []

    for skill in TECHNICAL_SKILLS:
        normalized_skill = skill.lower()
        pattern = (
            r"(?<![a-z0-9+#])"
            + re.escape(normalized_skill)
            + r"(?![a-z0-9+#])"
        )

        if re.search(pattern, normalized_text):
            found_skills.append(skill)

    return sorted(set(found_skills))
