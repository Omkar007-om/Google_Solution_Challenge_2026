"""
SAR Multi-Agent Backend — Structured Logging
=============================================
Provides a pre-configured, JSON-structured logger used across
the entire application.  Output format (json / text) is controlled
via the LOG_FORMAT environment variable.

Usage:
    from app.core.logger import logger
    logger.info("Pipeline started", extra={"request_id": rid})
"""

import logging
import sys

from pythonjsonlogger import json as json_logger

from app.config import get_settings


def _build_logger(name: str = "sar") -> logging.Logger:
    """Create and configure the application logger.

    Returns:
        A configured ``logging.Logger`` instance with the
        appropriate handler and formatter attached.
    """
    settings = get_settings()
    log = logging.getLogger(name)
    log.setLevel(settings.log_level.upper())

    # Avoid duplicate handlers on reload
    if log.handlers:
        return log

    handler = logging.StreamHandler(sys.stdout)

    if settings.log_format == "json":
        formatter = json_logger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level"},
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


# Module-level singleton — import `logger` anywhere
logger = _build_logger()
