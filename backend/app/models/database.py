import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.config import DATABASE_PATH


def _connect() -> sqlite3.Connection:
    database_path = Path(DATABASE_PATH)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    """
    Create the local SQLite tables needed by the API.
    """
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                stored_filename TEXT,
                email TEXT,
                phone TEXT,
                skills TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_resume_analysis(
    filename: str,
    stored_filename: str,
    email: str | None,
    phone: str | None,
    skills: list[str],
    text: str,
) -> int:
    """
    Persist a parsed resume and return its stable database ID.
    """
    init_database()
    created_at = datetime.now(UTC).isoformat()

    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO resumes (
                filename,
                stored_filename,
                email,
                phone,
                skills,
                text,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                filename,
                stored_filename,
                email,
                phone,
                json.dumps(skills),
                text,
                created_at,
            ),
        )

        return int(cursor.lastrowid)


def _resume_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "filename": row["filename"],
        "stored_filename": row["stored_filename"],
        "email": row["email"],
        "phone": row["phone"],
        "skills": json.loads(row["skills"]),
        "text": row["text"],
        "created_at": row["created_at"],
    }


def get_resume_analysis(resume_id: int) -> dict[str, Any] | None:
    """
    Return one persisted resume analysis by ID.
    """
    init_database()

    with _connect() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                filename,
                stored_filename,
                email,
                phone,
                skills,
                text,
                created_at
            FROM resumes
            WHERE id = ?
            """,
            (resume_id,),
        ).fetchone()

    if row is None:
        return None

    return _resume_row_to_dict(row)


def get_latest_resume_analysis() -> dict[str, Any] | None:
    """
    Return the most recently persisted resume analysis.
    """
    init_database()

    with _connect() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                filename,
                stored_filename,
                email,
                phone,
                skills,
                text,
                created_at
            FROM resumes
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

    if row is None:
        return None

    return _resume_row_to_dict(row)
