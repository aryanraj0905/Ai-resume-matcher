import re

from app.data.skills import TECHNICAL_SKILLS
from app.services.sections import split_into_blocks, split_sections, strip_bullet

EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
PHONE_PATTERN = r"(?:\+91[- ]?)?[6-9]\d{9}"
GITHUB_PATTERN = r"(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_-]+)"
LINKEDIN_PATTERN = r"(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9_-]+)/?"

DEGREE_KEYWORDS = (
    r"Bachelor(?:'s)?|Master(?:'s)?|B\.?\s?Tech|M\.?\s?Tech|B\.?E\.?|M\.?E\.?|"
    r"B\.?Sc\.?|M\.?Sc\.?|BCA|MCA|MBA|Ph\.?D\.?|Diploma|Associate(?:'s)?|LLB|LLM|B\.?A\.?|M\.?A\.?"
)
DEGREE_PATTERN = re.compile(rf"(?:{DEGREE_KEYWORDS})[^\n]*", re.IGNORECASE)
YEAR_PATTERN = re.compile(r"(19|20)\d{2}")
DATE_RANGE_PATTERN = re.compile(
    r"([A-Za-z]{3,9}\.?\s?\d{4}|\d{4})\s*(?:-|–|to)\s*([A-Za-z]{3,9}\.?\s?\d{4}|\d{4}|Present|Current)",
    re.IGNORECASE,
)
YEARS_EXPERIENCE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?experience", re.IGNORECASE
)
METRIC_PATTERN = re.compile(r"\d+(\.\d+)?\s*%|\$\d|\b\d{2,}\b")
# Matches only profile-link URLs (not general "word.tld" text) so real skills
# like "Node.js" are never accidentally stripped before skill matching.
PROFILE_URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?(?:github|linkedin)\.com/\S+", re.IGNORECASE
)

ACTION_VERB_PREFIXES = (
    "built", "developed", "implemented", "designed", "created", "led", "managed",
    "reduced", "increased", "improved", "optimized", "automated", "wrote", "deployed",
    "integrated", "achieved", "collaborated", "architected", "launched", "migrated",
    "refactored", "maintained", "mentored", "coordinated", "spearheaded", "delivered",
    "engineered", "analyzed", "researched", "tested", "debugged", "monitored",
    "configured", "established", "streamlined", "enhanced", "authored", "trained",
)


def extract_email(text: str) -> str | None:
    """Extract the first email address from the resume."""
    match = re.search(EMAIL_PATTERN, text)
    return match.group() if match else None


def extract_phone(text: str) -> str | None:
    """Extract an Indian phone number."""
    match = re.search(PHONE_PATTERN, text)
    return match.group() if match else None


def extract_github(text: str) -> str | None:
    """Extract a GitHub profile URL, normalized to https://github.com/<user>."""
    match = re.search(GITHUB_PATTERN, text, re.IGNORECASE)
    if not match:
        return None
    return f"https://github.com/{match.group(1)}"


def extract_linkedin(text: str) -> str | None:
    """Extract a LinkedIn profile URL, normalized to https://linkedin.com/in/<user>."""
    match = re.search(LINKEDIN_PATTERN, text, re.IGNORECASE)
    if not match:
        return None
    return f"https://linkedin.com/in/{match.group(1)}"


def extract_skills(text: str, skill_bank: list[str] | None = None) -> list[str]:
    """Extract technical (and domain) skills from free-form text."""
    # Strip profile URLs first so links (e.g. github.com/user) don't create
    # false-positive skill matches such as "GitHub" from the URL itself.
    normalized_text = PROFILE_URL_PATTERN.sub(" ", text).lower()
    found_skills = []

    for skill in skill_bank or TECHNICAL_SKILLS:
        normalized_skill = skill.lower()
        pattern = (
            r"(?<![a-z0-9+#])"
            + re.escape(normalized_skill)
            + r"(?![a-z0-9+#])"
        )

        if re.search(pattern, normalized_text):
            found_skills.append(skill)

    return sorted(set(found_skills))


def extract_years_of_experience(text: str) -> float | None:
    """Extract a stated total years-of-experience figure, if present."""
    matches = [float(match.group(1)) for match in YEARS_EXPERIENCE_PATTERN.finditer(text)]
    return max(matches) if matches else None


def extract_education(text: str) -> list[dict[str, str | None]]:
    """
    Extract education entries (degree, institution guess, year) from a resume.

    Falls back to scanning the whole document for degree keywords when no
    dedicated "Education" section header is found.
    """
    sections = split_sections(text)
    search_space = sections.get("education", text)

    entries: list[dict[str, str | None]] = []
    seen_lines: set[str] = set()

    for block in split_into_blocks(search_space):
        for line in block.splitlines():
            cleaned_line = strip_bullet(line)
            degree_match = DEGREE_PATTERN.search(cleaned_line)

            if not degree_match or cleaned_line in seen_lines:
                continue

            seen_lines.add(cleaned_line)
            year_match = YEAR_PATTERN.search(cleaned_line)
            parts = [part.strip() for part in cleaned_line.split(",") if part.strip()]
            institution = parts[1] if len(parts) > 1 else None

            entries.append(
                {
                    "degree": degree_match.group().strip(),
                    "institution": institution,
                    "year": year_match.group() if year_match else None,
                    "raw_text": cleaned_line,
                }
            )

    return entries


def extract_certifications(text: str) -> list[str]:
    """Extract certification names from a dedicated Certifications section."""
    sections = split_sections(text)
    section_text = sections.get("certifications")

    if not section_text:
        return []

    certifications = []

    for block in split_into_blocks(section_text):
        for line in block.splitlines():
            cleaned_line = strip_bullet(line)
            if cleaned_line and len(cleaned_line) <= 140:
                certifications.append(cleaned_line)

    return certifications


def _looks_like_description_line(line: str) -> bool:
    """Heuristic: bullet/description lines usually start with a lowercase word or an action verb."""
    if not line:
        return False
    if line[0].islower():
        return True
    return line.lower().startswith(ACTION_VERB_PREFIXES)


def _group_entries(section_text: str) -> list[dict[str, str | list[str] | None]]:
    """
    Group a section's raw lines into entries without relying on blank lines.

    A new entry starts at a non-description-looking line, but only once the
    current entry has already accumulated some content (a duration or bullet
    points) -- this keeps a title line and its immediately-following date
    range or bullets together even when the PDF has no blank-line spacing.
    A blank line always closes the current entry.
    """
    entries: list[dict[str, str | list[str] | None]] = []
    current: dict[str, str | list[str] | None] | None = None

    for raw_line in section_text.splitlines():
        if not raw_line.strip():
            current = None
            continue

        line = strip_bullet(raw_line)
        if not line:
            continue

        date_match = DATE_RANGE_PATTERN.search(line)
        is_description = _looks_like_description_line(line) and not date_match

        starts_new_entry = current is None or (
            not is_description
            and not date_match
            and (current["description"] or current["duration"])
        )

        if starts_new_entry:
            current = {"title": line, "duration": None, "description": []}
            entries.append(current)
            continue

        if date_match and current["duration"] is None:
            current["duration"] = date_match.group().strip()
            remainder = (line[: date_match.start()] + line[date_match.end():]).strip(" -|,")
            if remainder:
                current["description"].append(remainder)
            continue

        current["description"].append(line)

    return entries


def extract_experience(text: str) -> list[dict[str, str | list[str] | None]]:
    """
    Extract work experience entries from a dedicated Experience section.

    Each entry captures a best-effort title/company header line, a duration
    (when a date range is detected), and the bullet points describing it.
    """
    sections = split_sections(text)
    section_text = sections.get("experience")

    if not section_text:
        return []

    return _group_entries(section_text)


def extract_projects(text: str) -> list[dict[str, str | list[str] | None]]:
    """
    Extract project entries from a dedicated Projects section.

    Each entry captures a project name, description bullets, and the
    technologies detected in that project's text.
    """
    sections = split_sections(text)
    section_text = sections.get("projects")

    if not section_text:
        return []

    entries = _group_entries(section_text)

    for entry in entries:
        entry["name"] = entry.pop("title")
        project_text = entry["name"] + " " + " ".join(entry["description"])
        entry["technologies"] = extract_skills(project_text)
        entry.pop("duration", None)

    return entries


def has_measurable_achievements(lines: list[str]) -> bool:
    """Check whether any of the given bullet lines contain a quantified result."""
    return any(METRIC_PATTERN.search(line) for line in lines)


def extract_job_sections(description: str) -> dict[str, str]:
    """Split a job description into requirements/preferred/responsibilities text."""
    return split_sections(description)


def build_job_core_text(description: str) -> str:
    """
    Build a focused "what this role actually needs" text for semantic scoring.

    Job postings often bury the substantive requirements/responsibilities
    under boilerplate (company blurbs, benefits, EEO statements) or dilute
    them with a long "nice to have" wishlist. Using only the single most
    specific section available keeps the comparison focused and avoids
    watering down a genuinely strong match with unrelated bonus items.
    """
    sections = extract_job_sections(description)

    for key in ("responsibilities", "requirements", "preferred"):
        if sections.get(key):
            return sections[key]

    return description


def extract_required_and_preferred_skills(
    description: str,
) -> tuple[list[str], list[str]]:
    """
    Split job-required skills into "required" and "preferred" buckets.

    When the job description does not have distinguishable sections, every
    detected skill is treated as required.
    """
    sections = extract_job_sections(description)
    preferred_text = sections.get("preferred", "")
    preferred_skills = extract_skills(preferred_text) if preferred_text else []

    required_text = (
        sections.get("requirements", "")
        or sections.get("responsibilities", "")
        or description
    )
    required_skills = extract_skills(required_text)

    # Anything detected only in the "preferred" section shouldn't also count
    # as required.
    required_skills = [
        skill for skill in required_skills if skill not in preferred_skills
    ]

    if not required_skills and not preferred_skills:
        required_skills = extract_skills(description)

    return required_skills, preferred_skills
