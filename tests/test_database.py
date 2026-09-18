from database import get_recent_analyses, init_db, save_analysis


def test_save_analysis_and_read_back(tmp_path):
    db_path = tmp_path / "test_resume_analyzer.db"

    init_db(db_path)
    row_id = save_analysis(
        "resume.pdf",
        "Software Engineer",
        82,
        db_path=db_path,
    )

    rows = get_recent_analyses(db_path=db_path)

    assert row_id == 1
    assert len(rows) == 1
    assert rows[0]["resume_name"] == "resume.pdf"
    assert rows[0]["job_title"] == "Software Engineer"
    assert rows[0]["match_score"] == 82


def test_recent_analyses_returns_newest_first(tmp_path):
    db_path = tmp_path / "test_resume_analyzer.db"

    save_analysis("a.pdf", "Role A", 50, db_path=db_path)
    save_analysis("b.pdf", "Role B", 75, db_path=db_path)

    rows = get_recent_analyses(limit=2, db_path=db_path)

    assert rows[0]["resume_name"] == "b.pdf"
    assert rows[1]["resume_name"] == "a.pdf"


def test_match_score_validation(tmp_path):
    db_path = tmp_path / "test_resume_analyzer.db"

    try:
        save_analysis("resume.pdf", "Role", 101, db_path=db_path)
    except ValueError as exc:
        assert "0 to 100" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid match score")


def test_resume_name_validation(tmp_path):
    db_path = tmp_path / "test_resume_analyzer.db"

    try:
        save_analysis("", "Role", 80, db_path=db_path)
    except ValueError as exc:
        assert "resume_name is required" in str(exc)
    else:
        raise AssertionError("Expected ValueError for empty resume name")
