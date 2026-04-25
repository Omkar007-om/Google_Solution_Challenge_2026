"""
SAR Multi-Agent Backend — Application Configuration
====================================================
Centralized settings management via pydantic-settings.
All values are loaded from environment variables / .env file.

See ``.env.example`` for the full list of supported variables.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables."""

    # ── Application ──────────────────────────────────────
    app_name: str = "SAR-Multi-Agent-Backend"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True

    # ── Server ───────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # ── Logging ──────────────────────────────────────────
    log_level: str = "INFO"
    log_format: str = "json"  # "json" | "text"

    # ── Cache ────────────────────────────────────────────
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    cache_max_size: int = 128

    # ── Agent ────────────────────────────────────────────
    agent_timeout_seconds: int = 30

    # ── Rate Limiting (requests per minute) ──────────────
    rate_limit_rpm: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()
