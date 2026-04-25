"""
NEXUS 2.0 — SAR Audit Trail Database
SQLite database setup and CRUD operations for the SAR_Audit table.
"""

import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

# Database file lives alongside this module
DB_PATH = os.path.join(os.path.dirname(__file__), "nexus_audit.db")


@contextmanager
def get_db():
    """Context manager for SQLite connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # dict-like access
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Create the SAR_Audit table if it doesn't exist.
    Called once at application startup.
    """
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS SAR_Audit (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id         TEXT    NOT NULL UNIQUE,
                raw_alert_data  TEXT    NOT NULL,          -- JSON blob
                masked_data     TEXT    DEFAULT '{}',      -- JSON blob
                pii_mapping     TEXT    DEFAULT '{}',      -- JSON blob
                detected_typology TEXT  DEFAULT '',
                typology_analysis TEXT  DEFAULT '',
                draft_sar_masked TEXT   DEFAULT '',
                final_sar_clean  TEXT   DEFAULT '',
                compliance_score INTEGER DEFAULT 0,
                audit_log       TEXT    DEFAULT '[]',      -- JSON array of dicts
                status          TEXT    DEFAULT 'pending', -- pending | processing | completed | failed
                created_at      TEXT    NOT NULL,
                updated_at      TEXT    NOT NULL
            )
        """)
        conn.commit()
    print(f"[DB] SAR_Audit table ready at {DB_PATH}")


# ──────────────────────────────────────────────
#  CRUD helpers
# ──────────────────────────────────────────────

def insert_case(case_id: str, raw_alert_data: dict) -> dict:
    """Insert a new SAR case and return the created row."""
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO SAR_Audit (case_id, raw_alert_data, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (case_id, json.dumps(raw_alert_data), now, now),
        )
        conn.commit()
    return get_case(case_id)


def update_case(case_id: str, **fields) -> dict:
    """
    Update arbitrary columns for a case.
    JSON-serialisable values (dict/list) are auto-dumped.
    """
    now = datetime.utcnow().isoformat()
    set_clauses = []
    values = []
    for key, val in fields.items():
        set_clauses.append(f"{key} = ?")
        values.append(json.dumps(val) if isinstance(val, (dict, list)) else val)
    set_clauses.append("updated_at = ?")
    values.append(now)
    values.append(case_id)

    with get_db() as conn:
        conn.execute(
            f"UPDATE SAR_Audit SET {', '.join(set_clauses)} WHERE case_id = ?",
            values,
        )
        conn.commit()
    return get_case(case_id)


def get_case(case_id: str) -> dict | None:
    """Fetch a single case by case_id, with JSON fields parsed."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM SAR_Audit WHERE case_id = ?", (case_id,)
        ).fetchone()
    if row is None:
        return None
    return _row_to_dict(row)


def get_all_cases() -> list[dict]:
    """Return all cases (summary view)."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, case_id, detected_typology, compliance_score, status, created_at, updated_at "
            "FROM SAR_Audit ORDER BY id DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a plain dict, parsing JSON columns."""
    d = dict(row)
    for json_col in ("raw_alert_data", "masked_data", "pii_mapping", "audit_log"):
        if json_col in d and isinstance(d[json_col], str):
            try:
                d[json_col] = json.loads(d[json_col])
            except json.JSONDecodeError:
                pass
    return d
