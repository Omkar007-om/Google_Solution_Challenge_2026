"""
SAR Multi-Agent Backend — Utility Helpers
==========================================
Shared helper functions used across the application.
"""

from __future__ import annotations

import time
from functools import wraps
from typing import Any

from app.core.logger import logger


def timed(label: str | None = None):
    """Decorator that logs the execution duration of an async function.

    Args:
        label: Optional custom label for the log entry;
               defaults to the function name.

    Usage::

        @timed("my-operation")
        async def do_something():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tag = label or func.__name__
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            elapsed = round(time.perf_counter() - start, 4)
            logger.info("⏱  %s executed in %.4fs", tag, elapsed)
            return result
        return wrapper
    return decorator


def safe_serialize(obj: Any) -> Any:
    """Attempt JSON-safe serialisation of arbitrary objects.

    Falls back to ``str(obj)`` for non-serialisable types.
    """
    if isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [safe_serialize(item) for item in obj]
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    return str(obj)


def truncate(text: str, max_length: int = 500) -> str:
    """Truncate text with ellipsis if it exceeds ``max_length``."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Flatten a nested dictionary into dot-notation keys.

    Example::

        >>> flatten_dict({"a": {"b": 1, "c": {"d": 2}}})
        {"a.b": 1, "a.c.d": 2}
    """
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
