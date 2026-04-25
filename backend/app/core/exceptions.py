"""
SAR Multi-Agent Backend — Custom Exceptions
============================================
Defines a hierarchy of domain-specific exceptions so that
every layer can raise and catch errors with precision.

Exception Tree:
    SARBaseException
    ├── AgentError
    │   ├── AgentTimeoutError
    │   └── AgentRetryExhaustedError
    ├── PipelineError
    └── InputValidationError
"""

from __future__ import annotations

from typing import Any


class SARBaseException(Exception):
    """Root exception for all SAR backend errors.

    Attributes:
        message:    Human-readable error description.
        details:    Arbitrary context dict for debugging / API responses.
        request_id: Optional request-scoped correlation ID.
    """

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        details: Any = None,
        request_id: str | None = None,
    ):
        self.message = message
        self.details = details or {}
        self.request_id = request_id
        super().__init__(self.message)


# ── Agent-level errors ───────────────────────────────────

class AgentError(SARBaseException):
    """Raised when a single agent fails during execution."""

    def __init__(
        self,
        agent_name: str,
        message: str,
        details: Any = None,
        request_id: str | None = None,
    ):
        self.agent_name = agent_name
        super().__init__(
            message=f"[{agent_name}] {message}",
            details=details,
            request_id=request_id,
        )


class AgentTimeoutError(AgentError):
    """Raised when an agent exceeds its allowed execution time."""

    def __init__(self, agent_name: str, timeout_seconds: int):
        super().__init__(
            agent_name=agent_name,
            message=f"Agent timed out after {timeout_seconds}s",
            details={"timeout_seconds": timeout_seconds},
        )


class AgentRetryExhaustedError(AgentError):
    """Raised when an agent exhausts all retry attempts."""

    def __init__(self, agent_name: str, attempts: int, last_error: str):
        super().__init__(
            agent_name=agent_name,
            message=f"Failed after {attempts} attempt(s): {last_error}",
            details={"attempts": attempts, "last_error": last_error},
        )


# ── Pipeline-level errors ───────────────────────────────

class PipelineError(SARBaseException):
    """Raised when the pipeline orchestrator encounters a failure."""

    def __init__(
        self,
        message: str,
        failed_agent: str | None = None,
        details: Any = None,
        request_id: str | None = None,
    ):
        self.failed_agent = failed_agent
        super().__init__(
            message=message,
            details=details,
            request_id=request_id,
        )


# ── Validation errors ───────────────────────────────────

class InputValidationError(SARBaseException):
    """Raised when user-submitted input fails validation."""

    def __init__(self, message: str = "Invalid input data", details: Any = None):
        super().__init__(message=message, details=details)
