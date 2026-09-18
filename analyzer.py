import re


# Canonical display name -> common ways the skill may appear in a resume/job post.
# Keep this explicit for the prototype so matching behavior is easy to explain.
SKILL_ALIASES = {
    "Python": ["python"],
    "Java": ["java"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "c sharp"],
    "SQL": ["sql", "mysql", "postgresql", "postgres", "sql server"],
    "Git": ["git", "github", "gitlab"],
    "Docker": ["docker", "containerization", "containers"],
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


def _normalize(text: str) -> str:
    """Lowercase text and normalize whitespace for reliable matching."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_skill(text: str, aliases: list[str]) -> bool:
    """Return True when any alias appears as a standalone term/phrase."""
    for alias in aliases:
        alias = alias.lower().strip()

        # Skill names with punctuation such as C++ and C# are easier and safer
        # to detect with escaped literal matching plus loose boundaries.
        if any(ch in alias for ch in "+#"):
            pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"
        else:
            pattern = rf"(?<!\w){re.escape(alias)}(?!\w)"

        if re.search(pattern, text):
            return True

    return False


def _find_skills(text: str) -> list[str]:
    """Return recognized canonical skill names found in text."""
    normalized = _normalize(text)
    return [
        skill
        for skill, aliases in SKILL_ALIASES.items()
        if _contains_skill(normalized, aliases)
    ]


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Compare resume text with a job description.

    Returns exactly:
      - match_score: integer percentage from 0-100
      - matching_skills: requested skills found in the resume
      - missing_skills: requested skills not identified in the resume
      - suggestions: truthful improvement suggestions

    Missing skills are never presented as experience the applicant possesses.
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
            f"{skill} is requested for this position but was not identified "
            "on your resume. If you have this experience, consider adding it."
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
