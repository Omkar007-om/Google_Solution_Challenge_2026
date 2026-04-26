"""
indexer.py — seed the pgvector DB with embeddings from all PDF docs.

Usage:
    python -m rag.indexer

Walks rag/docs/ recursively, extracts text from every PDF,
chunks it, embeds with SentenceTransformer, and upserts into sar_documents.
Re-runs are idempotent — existing rows for a file are deleted before re-indexing.

Requires env var:
    VECTOR_DB_URL  — postgres connection string
                     e.g. postgresql://user:pass@host:5432/dbname
"""

import os
from pathlib import Path

import pdfplumber
import psycopg2

from rag.embeddings import embed_batch
from config import VECTOR_DB_URL

DOCS_DIR   = Path(__file__).resolve().parent / "docs"
CHUNK_SIZE    = 1200   # characters per chunk (~300 words)
CHUNK_OVERLAP = 150    # overlap to preserve context across chunk boundaries


# ── helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(path: Path) -> str:
    """Extract all text from a PDF using pdfplumber."""
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(_sanitise(text.strip()))
    return "\n\n".join(pages)


def _sanitise(text: str) -> str:
    """Strip NUL bytes and other control chars that Postgres rejects."""
    return text.replace("\x00", "").replace("\x0c", " ")


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = _sanitise(text)
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if len(c) > 80]  # drop tiny trailing fragments


def _relative_label(path: Path) -> str:
    """Return a human-readable label like 'typology/structuring.pdf'."""
    return str(path.relative_to(DOCS_DIR))


# ── main indexer ──────────────────────────────────────────────────────────────

def index_documents():
    db_url = VECTOR_DB_URL or os.environ.get("VECTOR_DB_URL")
    if not db_url:
        raise EnvironmentError("VECTOR_DB_URL environment variable is not set.")

    conn = psycopg2.connect(db_url)
    cur  = conn.cursor()

    pdf_files = sorted(DOCS_DIR.rglob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found under {DOCS_DIR}")
        return

    print(f"Found {len(pdf_files)} PDF files under {DOCS_DIR}\n")
    total_chunks = 0

    for pdf_path in pdf_files:
        label = _relative_label(pdf_path)

        # extract text
        try:
            text = extract_text_from_pdf(pdf_path)
        except Exception as e:
            print(f"  SKIP  {label} — could not extract text: {e}")
            continue

        if not text.strip():
            print(f"  SKIP  {label} — no extractable text (scanned PDF?)")
            continue

        chunks = chunk_text(text)
        if not chunks:
            print(f"  SKIP  {label} — no usable chunks after splitting")
            continue

        # delete existing rows for this file so re-runs are idempotent
        cur.execute("DELETE FROM sar_documents WHERE filename = %s", (label,))

        # embed all chunks in one batch call
        embeddings = embed_batch(chunks)

        for chunk, embedding in zip(chunks, embeddings):
            cur.execute(
                "INSERT INTO sar_documents (filename, chunk_text, embedding) "
                "VALUES (%s, %s, %s)",
                (label, chunk, embedding),
            )

        conn.commit()
        total_chunks += len(chunks)
        print(f"  OK    {label} — {len(chunks)} chunks")

    cur.close()
    conn.close()
    print(f"\nIndexing complete. {total_chunks} total chunks across {len(pdf_files)} files.")


if __name__ == "__main__":
    index_documents()
