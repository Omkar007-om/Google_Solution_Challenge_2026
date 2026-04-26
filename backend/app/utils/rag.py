"""Lightweight local RAG retrieval for AML/SAR guidance."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.logger import logger


KNOWLEDGE_PATH = Path(__file__).resolve().parents[1] / "data" / "aml_knowledge_base.json"


def retrieve_aml_context(query: str, tags: list[str] | None = None, top_k: int = 3) -> list[dict[str, Any]]:
    """Return the most relevant local AML knowledge snippets."""

    try:
        query_tokens = _tokens(query)
        requested_tags = {str(tag).lower() for tag in tags or [] if tag}
        scored = []

        for doc in _load_knowledge_base():
            doc_tags = {str(tag).lower() for tag in doc.get("tags", [])}
            searchable = " ".join([
                str(doc.get("title", "")),
                str(doc.get("category", "")),
                " ".join(str(tag) for tag in doc.get("tags", [])),
                str(doc.get("content", "")),
            ])
            token_score = len(query_tokens & _tokens(searchable))
            tag_score = len(requested_tags & doc_tags) * 4
            score = token_score + tag_score
            if score:
                scored.append((score, doc))

        ranked = sorted(scored, key=lambda item: item[0], reverse=True)[:max(top_k, 0)]
        return [
            {
                "id": str(doc.get("id", "UNKNOWN")),
                "title": str(doc.get("title", "Untitled guidance")),
                "category": str(doc.get("category", "AML guidance")),
                "content": str(doc.get("content", "")),
                "matched_score": score,
            }
            for score, doc in ranked
            if doc.get("content")
        ]
    except Exception as exc:
        logger.warning("RAG retrieval skipped: %s", exc)
        return []


@lru_cache(maxsize=1)
def _load_knowledge_base() -> list[dict[str, Any]]:
    try:
        with KNOWLEDGE_PATH.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except FileNotFoundError:
        logger.warning("RAG knowledge base not found at %s", KNOWLEDGE_PATH)
        return []
    except json.JSONDecodeError as exc:
        logger.warning("RAG knowledge base is invalid JSON: %s", exc)
        return []

    if not isinstance(payload, list):
        logger.warning("RAG knowledge base must be a list of documents")
        return []
    return [doc for doc in payload if isinstance(doc, dict)]


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9_]+", str(text).lower())
        if len(token) > 2
    }
