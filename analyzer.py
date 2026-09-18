import re


# Canonical skill -> explicit names/aliases that count as an exact match.
SKILL_ALIASES = {
    "Python": ["python"],
    "Java": ["java"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "c sharp"],
    "SQL": ["sql", "mysql", "postgresql", "postgres", "sql server"],
    "Git": ["git", "github", "gitlab"],
    "Docker": ["docker"],
    "Linux": ["linux", "ubuntu"],
    "JavaScript": ["javascript", "java script", "js"],
    "HTML": ["html"],
    "CSS": ["css"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs", "node js"],
    "Streamlit": ["streamlit"],
    "Flask": ["flask"],
    "SQLite": ["sqlite"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure", "microsoft azure"],
    "MATLAB": ["matlab"],
    "Verilog": ["verilog", "systemverilog", "system verilog"],
    "VHDL": ["vhdl"],
    "FPGA": ["fpga", "field programmable gate array"],
    "MIPS": ["mips", "mips assembly"],
    "Machine Learning": ["machine learning", "ml"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Communication": ["communication", "written communication", "verbal communication"],
    "Teamwork": ["teamwork", "team work", "collaboration", "collaborative"],
    "Problem Solving": ["problem solving", "problem-solving", "troubleshooting"],
}

# Related evidence does NOT count as possessing the exact skill.
# It is weaker supporting evidence and is worth half credit in the prototype score.
RELATED_EVIDENCE = {
    "Git": ["version control", "source control"],
    "SQL": ["relational database", "relational databases", "database querying", "database queries"],
    "Docker": ["containerization", "containerized application", "containerized applications", "containers"],
    "Linux": ["unix", "shell scripting", "bash"],
    "AWS": ["cloud computing", "cloud infrastructure"],
    "Azure": ["cloud computing", "cloud infrastructure"],
    "Machine Learning": ["predictive model", "predictive modeling", "classification model"],
    "Data Analysis": ["data visualization", "data cleaning", "data processing"],
    "Communication": ["presentations", "technical writing", "public speaking"],
    "Teamwork": ["cross-functional", "worked with teams", "team projects"],
    "Problem Solving": ["debugging", "root cause analysis"],
}


def _normalize(text: str) -> str:
    """Lowercase text and normalize whitespace for reliable matching."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_phrase(text: str, phrases: list[str]) -> bool:
    """Return True when any phrase appears as a standalone term/phrase."""
    for phrase in phrases:
        phrase = phrase.lower().strip()
        pattern = rf"(?<!\w){re.escape(phrase)}(?!\w)"
        if re.search(pattern, text):
            return True
    return False


def _find_skills(text: str) -> list[str]:
    """Return canonical skills explicitly found in text."""
    normalized = _normalize(text)
    return [
        skill
        for skill, aliases in SKILL_ALIASES.items()
        if _contains_phrase(normalized, aliases)
    ]


def _find_related_evidence(resume_text: str, required_skill: str) -> list[str]:
    """Return related phrases found for a required skill."""
    normalized = _normalize(resume_text)
    evidence = []

    for phrase in RELATED_EVIDENCE.get(required_skill, []):
        if _contains_phrase(normalized, [phrase]):
            evidence.append(phrase)

    return evidence


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Compare resume text with a job description.

    Returns:
      - match_score: integer percentage from 0-100
      - matching_skills: exact requested skills found in the resume
      - related_skills: related evidence for a requested skill
      - missing_skills: requested skills with no exact or related evidence
      - suggestions: truthful improvement suggestions

    Scoring:
      exact match = 1.0 point
      related evidence = 0.5 point
      missing = 0 points

    Related evidence never claims that the applicant possesses the exact skill.
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
            "related_skills": [],
            "missing_skills": [],
            "suggestions": [
                "No recognized skills were found in the job description yet. "
                "Review the posting manually or expand the analyzer skill vocabulary."
            ],
        }

    resume_skills = set(_find_skills(resume_text))

    matching_skills = []
    related_skills = []
    missing_skills = []

    for skill in required_skills:
        if skill in resume_skills:
            matching_skills.append(skill)
            continue

        evidence = _find_related_evidence(resume_text, skill)
        if evidence:
            related_skills.append({
                "skill": skill,
                "evidence": evidence,
            })
        else:
            missing_skills.append(skill)

    exact_points = len(matching_skills)
    related_points = 0.5 * len(related_skills)
    match_score = round(
        (exact_points + related_points) / len(required_skills) * 100
    )

    suggestions = []

    if matching_skills:
        suggestions.append(
            "Emphasize relevant experience that demonstrates: "
            + ", ".join(matching_skills)
            + "."
        )

    for item in related_skills:
        evidence_text = ", ".join(item["evidence"])
        suggestions.append(
            f"{item['skill']} is requested. Your resume shows related evidence "
            f"({evidence_text}), but the exact skill is not explicitly listed. "
            "If you have direct experience, consider naming it clearly."
        )

    for skill in missing_skills:
        suggestions.append(
            f"{skill} is requested for this position but was not identified "
            "on your resume. If you have this experience, consider adding it."
        )

    if not related_skills and not missing_skills:
        suggestions.append(
            "All recognized requested skills were explicitly identified on your resume. "
            "Focus next on tailoring accomplishments and measurable results."
        )

    return {
        "match_score": match_score,
        "matching_skills": matching_skills,
        "related_skills": related_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
    }
