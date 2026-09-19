import sqlite3
from pathlib import Path


DB_PATH = Path("data") / "resume_analyzer.db"


def _connect(db_path=DB_PATH):
    """Create the database directory if needed and return a SQLite connection."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def init_db(db_path=DB_PATH):
    """Create the analyses table if it does not already exist."""
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_name TEXT NOT NULL,
                job_title TEXT,
                match_score INTEGER NOT NULL CHECK(match_score BETWEEN 0 AND 100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_analysis(
    resume_name: str,
    job_title: str,
    match_score: int,
    db_path=DB_PATH,
):
    """Persist minimal analysis metadata and return the new row id."""
    if not isinstance(resume_name, str) or not resume_name.strip():
        raise ValueError("resume_name is required.")

    if job_title is None:
        job_title = ""
    elif not isinstance(job_title, str):
        raise ValueError("job_title must be a string.")

    if not isinstance(match_score, int) or not 0 <= match_score <= 100:
        raise ValueError("match_score must be an integer from 0 to 100.")

    init_db(db_path)

    with _connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO analyses (resume_name, job_title, match_score)
            VALUES (?, ?, ?)
            """,
            (resume_name.strip(), job_title.strip(), match_score),
        )
        conn.commit()
        return cursor.lastrowid
    
    
def clear_analyses(db_path=DB_PATH):
    """Clears all analyses on display"""
    
    init_db(db_path)
    
    with _connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute(
            """
            DELETE FROM analyses
            """
        )
        conn.commit()
        


def get_recent_analyses(limit: int = 10, db_path=DB_PATH):
    """Return recent analyses as dictionaries, newest first."""
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer.")

    init_db(db_path)

    with _connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, resume_name, job_title, match_score, created_at
            FROM analyses
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]
