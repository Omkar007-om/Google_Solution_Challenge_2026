"""
Nexus 2.0 — PostgreSQL Database Layer
======================================
Async PostgreSQL connection pool for feedback and audit persistence.
"""

from __future__ import annotations

import json
from typing import Any

import asyncpg

from app.config import get_settings
from app.core.logger import logger

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the database connection pool."""
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=settings.database_pool_min,
            max_size=settings.database_pool_max,
        )
        logger.info("PostgreSQL connection pool created")
    return _pool


async def close_pool() -> None:
    """Close the database connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("PostgreSQL connection pool closed")


async def init_db() -> None:
    """Initialize database tables."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Feedback table for RLHF (Layer 5: Human Control)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                case_id VARCHAR(255) NOT NULL,
                analyst_id VARCHAR(255) NOT NULL,
                original_sar JSONB NOT NULL,
                edited_sar JSONB,
                outcome VARCHAR(50) CHECK (outcome IN ('true_positive', 'false_positive', 'pending')),
                analyst_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Audit logs for Glass-Box trail (Layer 4: Audit Brain)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                case_id VARCHAR(255) NOT NULL,
                pipeline_version VARCHAR(50) NOT NULL,
                audit_entries JSONB NOT NULL,
                shap_explanation JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_case_id ON feedback(case_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_analyst ON feedback(analyst_id)
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_case_id ON audit_logs(case_id)
        """)
        
        logger.info("Database tables initialized")


async def save_feedback(
    case_id: str,
    analyst_id: str,
    original_sar: dict[str, Any],
    edited_sar: dict[str, Any] | None,
    outcome: str | None,
    analyst_notes: str | None = None,
) -> int:
    """Save analyst feedback for RLHF.
    
    Returns:
        The ID of the inserted feedback record.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO feedback (case_id, analyst_id, original_sar, edited_sar, outcome, analyst_notes)
            VALUES ($1, $2, $3::jsonb, $4::jsonb, $5, $6)
            RETURNING id
            """,
            case_id,
            analyst_id,
            json.dumps(original_sar) if isinstance(original_sar, dict) else original_sar,
            json.dumps(edited_sar) if isinstance(edited_sar, dict) else edited_sar,
            outcome,
            analyst_notes,
        )
        logger.info("Feedback saved for case %s (id=%d)", case_id, row["id"])
        return row["id"]


async def save_audit_log(
    case_id: str,
    pipeline_version: str,
    audit_entries: list[dict[str, Any]],
    shap_explanation: dict[str, Any] | None,
) -> int:
    """Save glass-box audit trail.
    
    Returns:
        The ID of the inserted audit log record.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO audit_logs (case_id, pipeline_version, audit_entries, shap_explanation)
            VALUES ($1, $2, $3::jsonb, $4::jsonb)
            RETURNING id
            """,
            case_id,
            pipeline_version,
            json.dumps(audit_entries) if isinstance(audit_entries, list) else audit_entries,
            json.dumps(shap_explanation) if isinstance(shap_explanation, dict) else shap_explanation,
        )
        logger.info("Audit log saved for case %s (id=%d)", case_id, row["id"])
        return row["id"]


async def get_feedback_stats(analyst_id: str | None = None) -> dict[str, Any]:
    """Get feedback statistics for analytics."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        if analyst_id:
            row = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE outcome = 'true_positive') as true_positives,
                    COUNT(*) FILTER (WHERE outcome = 'false_positive') as false_positives,
                    COUNT(*) FILTER (WHERE outcome = 'pending') as pending
                FROM feedback
                WHERE analyst_id = $1
                """,
                analyst_id,
            )
        else:
            row = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE outcome = 'true_positive') as true_positives,
                    COUNT(*) FILTER (WHERE outcome = 'false_positive') as false_positives,
                    COUNT(*) FILTER (WHERE outcome = 'pending') as pending
                FROM feedback
                """,
            )
        return dict(row) if row else {"total": 0, "true_positives": 0, "false_positives": 0, "pending": 0}
