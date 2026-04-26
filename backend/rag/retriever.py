"""
retriever.py — cosine similarity search over sar_vector DB.

Two retrieval modes:
  retrieve(query, top_k)                    — searches entire table
  retrieve_from_folder(folder, query, top_k) — scoped to a subfolder prefix

Folder values match the subdirectory names used by the indexer:
  "typology"           → rag/docs/typology/
  "guideline how to"   → rag/docs/guideline how to/
  "sar case examples"  → rag/docs/sar case examples/
"""

import os
import psycopg2
from rag.embeddings import embed
from config import VECTOR_DB_URL


def _connect():
    return psycopg2.connect(VECTOR_DB_URL or os.environ["VECTOR_DB_URL"])


def retrieve(query: str, top_k: int = 2) -> list[str]:
    """Semantic search across the entire sar_documents table."""
    query_vec = embed(query)
    conn = _connect()
    cur  = conn.cursor()
    cur.execute(
        "SELECT chunk_text FROM sar_documents "
        "ORDER BY embedding <=> %s::vector LIMIT %s",
        (query_vec, top_k),
    )
    results = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return results


def retrieve_from_folder(folder: str, query: str, top_k: int = 2) -> list[str]:
    """
    Semantic search scoped to a specific subfolder.
    Normalises backslashes to forward slashes so Windows-indexed paths
    match correctly regardless of OS.
    """
    query_vec = embed(query)
    # Normalise separator — Windows indexer stores 'typology\\structuring.pdf'
    prefix = folder.replace("\\", "/").rstrip("/") + "/%"
    conn = _connect()
    cur  = conn.cursor()
    cur.execute(
        "SELECT chunk_text FROM sar_documents "
        "WHERE replace(filename, '\\', '/') LIKE %s "
        "ORDER BY embedding <=> %s::vector LIMIT %s",
        (prefix, query_vec, top_k),
    )
    results = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return results


def retrieve_with_scores(query: str, top_k: int = 2) -> list[dict]:
    """Full-table search that also returns cosine distance scores (for debugging)."""
    query_vec = embed(query)
    conn = _connect()
    cur  = conn.cursor()
    cur.execute(
        "SELECT chunk_text, embedding <=> %s::vector AS score "
        "FROM sar_documents ORDER BY score LIMIT %s",
        (query_vec, top_k),
    )
    results = [{"chunk": row[0], "score": round(float(row[1]), 4)} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return results