"""
EZChart — structured logging setup.

Uses structlog for structured logs, useful for
observability on free-tier hosting (Render, Oracle).
"""

import logging
import sys

import structlog

from src.config import settings


def setup_logging() -> None:
    """
    Configure stdlib logging + structlog.
    Call once at application startup (from main.py).
    """
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    # Silence noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
            if settings.is_debug
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "ezchart") -> structlog.stdlib.BoundLogger:
    """Get a structured logger. Usage: log = get_logger(__name__)"""
    return structlog.get_logger(name)