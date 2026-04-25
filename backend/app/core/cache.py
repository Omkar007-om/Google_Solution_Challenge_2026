"""
SAR Multi-Agent Backend — In-Memory LRU Cache
==============================================
A lightweight, async-safe TTL cache for pipeline results.
Keyed on a SHA-256 hash of the request payload so identical
inputs skip re-computation.

Design choices:
    • OrderedDict for O(1) LRU eviction
    • Threading lock for thread-safety under uvicorn workers
    • Per-entry TTL to auto-expire stale results
    • Hit/miss/evict counters for observability
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from threading import Lock
from typing import Any

from app.config import get_settings
from app.core.logger import logger


class TTLCache:
    """Thread-safe, size-bounded cache with per-entry TTL expiration.

    Attributes:
        max_size: Maximum number of entries.
        ttl:      Time-to-live in seconds for each cache entry.
    """

    def __init__(self, max_size: int | None = None, ttl: int | None = None):
        settings = get_settings()
        self.max_size = max_size or settings.cache_max_size
        self.ttl = ttl or settings.cache_ttl_seconds
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = Lock()

        # ── Observability counters ───────────────────────
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    # ── Public API ───────────────────────────────────────

    def get(self, key: str) -> Any | None:
        """Return cached value if present and not expired, else ``None``."""
        with self._lock:
            if key not in self._store:
                self._misses += 1
                return None
            ts, value = self._store[key]
            if time.time() - ts > self.ttl:
                del self._store[key]
                self._misses += 1
                logger.debug("Cache EXPIRED for key=%s", key[:12])
                return None
            # Move to end so LRU eviction works
            self._store.move_to_end(key)
            self._hits += 1
            logger.debug("Cache HIT for key=%s", key[:12])
            return value

    def set(self, key: str, value: Any) -> None:
        """Insert or update a cache entry."""
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = (time.time(), value)
            # Evict oldest entry when capacity is exceeded
            if len(self._store) > self.max_size:
                evicted_key, _ = self._store.popitem(last=False)
                self._evictions += 1
                logger.debug("Cache EVICT key=%s", evicted_key[:12])
        logger.debug("Cache SET for key=%s", key[:12])

    def clear(self) -> None:
        """Remove all entries."""
        with self._lock:
            self._store.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
        logger.info("Cache cleared")

    @property
    def size(self) -> int:
        """Current number of entries."""
        return len(self._store)

    @property
    def stats(self) -> dict[str, int]:
        """Snapshot of hit/miss/eviction counters."""
        return {
            "size": self.size,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": round(
                self._hits / max(self._hits + self._misses, 1) * 100, 1
            ),
        }

    # ── Helpers ──────────────────────────────────────────

    @staticmethod
    def make_key(payload: dict) -> str:
        """Produce a deterministic SHA-256 hash for a JSON-serializable dict."""
        raw = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()


# Module-level singleton
pipeline_cache = TTLCache()
