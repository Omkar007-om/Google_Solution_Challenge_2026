"""
SAR Multi-Agent Backend — Application Configuration
====================================================
Centralized settings management via pydantic-settings.
All values are loaded from environment variables / .env file.

See ``.env.example`` for the full list of supported variables.
"""

from functools import lru_cache

from pydantic import field_validator
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

    # ── Auth / JWT ───────────────────────────────────────
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "nexus-sar"
    jwt_audience: str = "nexus-sar-ui"
    jwt_access_token_exp_minutes: int = 60

    # Demo credentials (replace with real identity provider)
    auth_demo_username: str = "admin"
    auth_demo_password: str = "admin"

    # ── Database ───────────────────────────────────────────
    database_url: str = "postgresql://postgres:postgres@localhost:5432/nexus"
    database_pool_min: int = 1
    database_pool_max: int = 10

    # ── LLM API (Layer 3: Narrative Engine) ────────────────
    llm_api_key: str = ""
    llm_api_base: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2000
    llm_timeout_seconds: int = 60
    llm_enabled: bool = False

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "off", "false", "0", "no"}:
                return False
            if normalized in {"debug", "dev", "development", "on", "true", "1", "yes"}:
                return True
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()
