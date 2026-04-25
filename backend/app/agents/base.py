"""
SAR Multi-Agent Backend — Base Agent
=====================================
Abstract base class that every agent must extend.  Provides:
  • A consistent async interface  (``execute``)
  • Built-in timing & structured logging
  • Automatic error wrapping into ``AgentError``
  • Per-agent timeout enforcement via ``asyncio.wait_for``
  • Configurable retry with exponential backoff

To create a new agent, subclass ``BaseAgent`` and implement
``process(data)`` — that's it.
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any

from app.config import get_settings
from app.core.exceptions import AgentError, AgentTimeoutError, AgentRetryExhaustedError
from app.core.logger import logger


class BaseAgent(ABC):
    """Abstract base class for all SAR pipeline agents.

    Attributes:
        name:        Human-readable identifier for logging and tracing.
        retries:     Number of retry attempts on transient failures (0 = no retry).
        retry_delay: Base delay in seconds between retries (doubles each attempt).
    """

    name: str = "BaseAgent"
    retries: int = 0
    retry_delay: float = 0.5

    async def execute(self, data: Any) -> Any:
        """Run the agent with timeout, retries, timing, logging, and error handling.

        Args:
            data: Output from the previous agent (or raw user input for
                  the first agent in the pipeline).

        Returns:
            Transformed / enriched data for the next agent.

        Raises:
            AgentTimeoutError:        If execution exceeds the configured timeout.
            AgentRetryExhaustedError: If all retry attempts fail.
            AgentError:               Wraps any other exception thrown inside ``process``.
        """
        settings = get_settings()
        timeout = settings.agent_timeout_seconds
        max_attempts = 1 + self.retries
        last_error: str = ""

        for attempt in range(1, max_attempts + 1):
            logger.info(
                "▶  Agent [%s] started (attempt %d/%d)",
                self.name, attempt, max_attempts,
            )
            start = time.perf_counter()

            try:
                # Enforce per-agent timeout
                result = await asyncio.wait_for(
                    self.process(data),
                    timeout=timeout,
                )
                elapsed = round(time.perf_counter() - start, 4)
                logger.info("✔  Agent [%s] completed in %.4fs", self.name, elapsed)
                return result

            except asyncio.TimeoutError:
                elapsed = round(time.perf_counter() - start, 4)
                logger.error(
                    "⏰ Agent [%s] timed out after %.4fs (limit=%ds)",
                    self.name, elapsed, timeout,
                )
                raise AgentTimeoutError(
                    agent_name=self.name,
                    timeout_seconds=timeout,
                )

            except AgentError:
                raise  # Already wrapped — propagate as-is

            except Exception as exc:
                last_error = str(exc)
                elapsed = round(time.perf_counter() - start, 4)
                logger.warning(
                    "⚠  Agent [%s] attempt %d/%d failed (%.4fs): %s",
                    self.name, attempt, max_attempts, elapsed, last_error,
                )
                if attempt < max_attempts:
                    delay = self.retry_delay * (2 ** (attempt - 1))
                    logger.info("   Retrying in %.1fs…", delay)
                    await asyncio.sleep(delay)
                    continue

                # All attempts exhausted
                if self.retries > 0:
                    raise AgentRetryExhaustedError(
                        agent_name=self.name,
                        attempts=max_attempts,
                        last_error=last_error,
                    ) from exc

                raise AgentError(
                    agent_name=self.name,
                    message=last_error,
                    details={"input_snapshot": str(data)[:500]},
                ) from exc

        # Should never reach here, but satisfy the type checker
        raise AgentError(agent_name=self.name, message="Unexpected execution path")

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Core transformation logic — implement in subclass.

        Args:
            data: Incoming data from the previous pipeline stage.

        Returns:
            Processed / transformed data.
        """
        ...
