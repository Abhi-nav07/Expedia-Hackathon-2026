"""
Structured logging configuration.

Rules enforced here:
- Never log raw request bodies containing passwords/tokens (use `mask_sensitive`).
- JSON output in production for log aggregation; readable console output locally.
"""
import logging
import sys
from typing import Any, Dict

import structlog

from app.core.config import settings

# Keys that must never appear in logs, even accidentally
SENSITIVE_KEYS = {
    "password",
    "confirm_password",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "jwt_secret_key",
    "api_key",
    "openai_api_key",
    "gemini_api_key",
    "anthropic_api_key",
    "client_secret",
}


def mask_sensitive(_, __, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Structlog processor: redact any key that looks sensitive before it hits stdout."""
    for key in list(event_dict.keys()):
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "***REDACTED***"
    return event_dict


def configure_logging() -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.APP_DEBUG else logging.INFO,
    )

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        mask_sensitive,
    ]

    if settings.is_production:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if settings.APP_DEBUG else logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "app"):
    return structlog.get_logger(name)
