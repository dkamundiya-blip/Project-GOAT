"""
Project GOAT v0.1 — Structured Logging

Configures ``structlog`` for consistent, structured logging across the system.
Values of keys matching sensitive patterns (secret, password, token, key,
credential, api_key) are automatically redacted from all log output.
"""

from __future__ import annotations

import logging
import re
from typing import Any

import structlog

_SENSITIVE_PATTERN = re.compile(
    r"(secret|password|token|key|credential|api_key)", re.IGNORECASE
)


def _redact_sensitive(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Structlog processor that redacts values of sensitive-looking keys."""
    for key in list(event_dict.keys()):
        if _SENSITIVE_PATTERN.search(key):
            event_dict[key] = "***REDACTED***"
    return event_dict


def configure_logging(level: str = "INFO", json_output: bool = False) -> None:
    """Configure structured logging for the entire application.

    Call once at application startup. Subsequent calls reconfigure the
    global structlog pipeline.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_output: If True, render log lines as JSON; otherwise use
                     the human-readable console renderer.
    """
    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if json_output
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            _redact_sensitive,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(component: str) -> structlog.stdlib.BoundLogger:
    """Get a logger bound to a specific component name.

    Args:
        component: Component identifier (e.g. ``"collector"``, ``"storage"``).

    Returns:
        A bound structlog logger instance.
    """
    return structlog.get_logger(component=component)
