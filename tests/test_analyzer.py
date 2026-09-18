from analyzer import analyze_resume


def test_strong_match():
    resume = "Python, GitHub, PostgreSQL, Docker, Linux"
    job = "Python, Git, SQL, Docker, Linux"
    result = analyze_resume(resume, job)

    assert result["match_score"] == 100
    assert result["missing_skills"] == []
    assert result["related_skills"] == []


def test_synonyms_are_recognized():
    resume = "Worked with GitHub and PostgreSQL on Ubuntu systems."
    job = "Requires Git, SQL, and Linux."
    result = analyze_resume(resume, job)

    assert result["match_score"] == 100
    assert set(result["matching_skills"]) == {"Git", "SQL", "Linux"}


def test_partial_match():
    resume = "Python and Git"
    job = "Python, Git, Docker, SQL"
    result = analyze_resume(resume, job)

    assert result["match_score"] == 50
    assert set(result["matching_skills"]) == {"Python", "Git"}
    assert set(result["missing_skills"]) == {"Docker", "SQL"}


def test_related_experience_gets_half_credit():
    resume = "Used version control and relational databases in class projects."
    job = "Requires Git and SQL."
    result = analyze_resume(resume, job)

    assert result["match_score"] == 50
    assert result["matching_skills"] == []
    assert result["missing_skills"] == []

    related_names = {item["skill"] for item in result["related_skills"]}
    assert related_names == {"Git", "SQL"}


def test_related_experience_does_not_become_exact_match():
    resume = "Built containerized applications and used source control."
    job = "Requires Docker and Git."
    result = analyze_resume(resume, job)

    assert result["matching_skills"] == []
    assert {item["skill"] for item in result["related_skills"]} == {"Docker", "Git"}


def test_missing_skill_is_not_invented():
    resume = "Python and Git"
    job = "Python, Git, Docker"
    result = analyze_resume(resume, job)

    assert "Docker" in result["missing_skills"]
    assert any(
        "not identified on your resume" in suggestion
        for suggestion in result["suggestions"]
    )


def test_empty_resume_raises_error():
    try:
        analyze_resume("", "Python")
    except ValueError as exc:
        assert "Resume text is empty" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty resume")


def test_empty_job_description_raises_error():
    try:
        analyze_resume("Python", "")
    except ValueError as exc:
        assert "Job description is empty" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty job description")
