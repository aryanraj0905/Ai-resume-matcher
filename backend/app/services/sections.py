"""
Lightweight heuristics for splitting free-form resume and job description
text into labeled sections (education, experience, projects, ...).

Resumes and job posts rarely follow a single fixed format, so this module
relies on a curated list of common section header phrases rather than a full
NLP pipeline. It is intentionally simple and dependency-free so it stays fast
and predictable for every request.
"""

import re

SECTION_ALIASES: dict[str, list[str]] = {
    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "academic details",
        "educational qualifications",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "relevant experience",
    ],
    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "key projects",
        "notable projects",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses & certifications",
        "licenses and certifications",
        "courses & certifications",
        "professional certifications",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "key skills",
        "skills & tools",
    ],
    "responsibilities": [
        "responsibilities",
        "key responsibilities",
        "role & responsibilities",
        "what you will do",
        "what you'll do",
        "the role",
        "job duties",
        "duties",
    ],
    "requirements": [
        "requirements",
        "qualifications",
        "required qualifications",
        "minimum qualifications",
        "must have",
        "must-have skills",
        "what you need",
        "what we're looking for",
        "basic qualifications",
    ],
    "preferred": [
        "preferred qualifications",
        "preferred skills",
        "nice to have",
        "nice-to-have",
        "bonus points",
        "good to have",
    ],
}

_MAX_HEADER_LENGTH = 48


def _normalize_header_candidate(line: str) -> str:
    cleaned = line.strip().strip(":").strip()
    cleaned = re.sub(r"^[\-\*•#\s]+", "", cleaned)
    return cleaned.lower()


def _matches_alias(normalized_line: str) -> str | None:
    for section_name, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if normalized_line == alias or (
                normalized_line.startswith(alias)
                and len(normalized_line) <= len(alias) + 3
            ):
                return section_name
    return None


def split_sections(text: str) -> dict[str, str]:
    """
    Split resume or job description text into labeled sections.

    A line is treated as a section header when, once stripped of bullets and
    punctuation, it closely matches one of the known section aliases and is
    short enough to plausibly be a heading rather than a sentence.

    Returns:
        A mapping of section name -> the raw text found under that heading.
        Sections that were not detected are simply absent from the mapping.
    """
    lines = text.splitlines()
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in lines:
        candidate = _normalize_header_candidate(line)

        if candidate and len(candidate) <= _MAX_HEADER_LENGTH:
            matched_section = _matches_alias(candidate)
        else:
            matched_section = None

        if matched_section:
            current_section = matched_section
            sections.setdefault(current_section, [])
            continue

        if current_section:
            sections[current_section].append(line)

    return {
        name: "\n".join(section_lines).strip()
        for name, section_lines in sections.items()
        if "\n".join(section_lines).strip()
    }


def split_into_blocks(section_text: str) -> list[str]:
    """
    Split a section's text into entry blocks separated by blank lines.

    Falls back to one block per line when the section has no blank-line
    separators (common in tightly formatted PDFs).
    """
    raw_blocks = re.split(r"\n\s*\n", section_text.strip())
    blocks = [block.strip() for block in raw_blocks if block.strip()]

    if len(blocks) > 1:
        return blocks

    # No blank-line separation was detected; treat each non-empty line as
    # its own entry so callers still get reasonably granular results.
    return [line.strip() for line in section_text.splitlines() if line.strip()]


def strip_bullet(line: str) -> str:
    return re.sub(r"^[\-\*•●▪–\s]+", "", line).strip()
