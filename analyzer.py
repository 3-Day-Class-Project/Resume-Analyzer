import re


# Small, explicit vocabulary for the first prototype.
# We can expand this after the basic end-to-end flow is working.
SKILL_ALIASES = {
    "python": ["python"],
    "java": ["java"],
    "c++": ["c++", "cpp"],
    "c": [" c "],
    "sql": ["sql"],
    "git": ["git", "github"],
    "docker": ["docker"],
    "linux": ["linux"],
    "javascript": ["javascript", "js"],
    "html": ["html"],
    "css": ["css"],
    "streamlit": ["streamlit"],
    "flask": ["flask"],
    "sqlite": ["sqlite"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "machine learning": ["machine learning", "ml"],
    "data analysis": ["data analysis", "data analytics"],
    "communication": ["communication"],
    "teamwork": ["teamwork", "team work", "collaboration"],
    "problem solving": ["problem solving", "problem-solving"],
}


def _normalize(text: str) -> str:
    """Lowercase text and normalize whitespace for simple matching."""
    return " " + re.sub(r"\s+", " ", text.lower()).strip() + " "


def _contains_skill(text: str, aliases: list[str]) -> bool:
    """Return True when any alias appears in normalized text."""
    for alias in aliases:
        alias = alias.lower()

        # Symbols such as C++ do not work well with ordinary word boundaries,
        # so use direct matching for those.
        if any(ch in alias for ch in "+#"):
            if alias in text:
                return True
        else:
            pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"
            if re.search(pattern, text):
                return True

    return False


def _find_skills(text: str) -> list[str]:
    """Return recognized skills found in text."""
    normalized = _normalize(text)
    return [
        skill
        for skill, aliases in SKILL_ALIASES.items()
        if _contains_skill(normalized, aliases)
    ]


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Compare resume text with a job description.

    Returns a dictionary containing:
      - match_score: integer percentage from 0-100
      - matching_skills: requested skills found in the resume
      - missing_skills: requested skills not identified in the resume
      - suggestions: truthful improvement suggestions

    This first prototype intentionally does not invent experience. A missing
    skill is flagged so the user can decide whether they genuinely possess it.
    """
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("Job description is empty.")

    required_skills = _find_skills(job_description)

    if not required_skills:
        return {
            "match_score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "suggestions": [
                "No recognized skills were found in the job description yet. "
                "Review the posting manually or expand the analyzer skill vocabulary."
            ],
        }

    resume_skills = set(_find_skills(resume_text))

    matching_skills = [
        skill for skill in required_skills if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in required_skills if skill not in resume_skills
    ]

    match_score = round(
        len(matching_skills) / len(required_skills) * 100
    )

    suggestions = []

    if matching_skills:
        suggestions.append(
            "Emphasize relevant experience that demonstrates: "
            + ", ".join(matching_skills)
            + "."
        )

    for skill in missing_skills:
        suggestions.append(
            f"{skill.title()} is requested for this position but was not "
            "identified on your resume. If you have this experience, "
            "consider adding it."
        )

    if not missing_skills:
        suggestions.append(
            "All recognized requested skills were identified on your resume. "
            "Focus next on tailoring accomplishments and measurable results."
        )

    return {
        "match_score": match_score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
    }
