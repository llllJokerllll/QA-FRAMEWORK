"""
Logging Configuration with Structlog

Provides structured logging configuration for the QA-Framework Dashboard.
Supports both console (dev) and JSON (prod) output formats with context binding for request tracing.
"""

import logging
import sys
import os
from typing import Any
from contextvars import ContextVar
import structlog
from structlog.types import Processor

# Context variable for request ID tracking
request_id_context: ContextVar[str] = ContextVar("request_id", default="")


def add_request_id_processor(logger, method_name, event_dict):
    """Add request_id from context to all log entries."""
    request_id = request_id_context.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def configure_logging(
    log_level: str = "INFO", json_format: bool = None, environment: str = None
) -> None:
    """
    Configure structured logging with structlog.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: If True, use JSON format. If None, auto-detect from environment.
        environment: Environment name (dev, prod, etc.)
    """
    # Auto-detect format based on environment if not specified
    if json_format is None:
        env = environment or os.getenv("ENVIRONMENT", "development").lower()
        json_format = env in ("production", "prod", "staging")

    # Shared processors for both logging and structlog
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.UnicodeDecoder(),
        add_request_id_processor,
    ]

    # Configure structlog
    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Choose output format based on configuration
    if json_format:
        # JSON format for production
        formatter_processors = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console format for development
        formatter_processors = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    # Configure standard logging
    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT already contain
        # structlog information.
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            add_request_id_processor,
        ],
        # These run on ALL entries after the pre_chain is done.
        processors=formatter_processors,
    )

    # Configure root logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = []  # Clear existing handlers
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.getLevelName(log_level))

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured structlog logger.

    Args:
        name: Logger name (usually __name__)

    Returns:
        A configured structlog logger instance
    """
    return structlog.get_logger(name)


def set_request_id(request_id: str) -> None:
    """
    Set the request ID for the current context.
    This ID will be included in all subsequent log entries.

    Args:
        request_id: Unique request identifier
    """
    request_id_context.set(request_id)


def clear_request_id() -> None:
    """Clear the request ID from the current context."""
    request_id_context.set("")


def get_request_id() -> str:
    """Get the current request ID from context."""
    return request_id_context.get()


# Example usage
if __name__ == "__main__":
    # Configure logging for development (console)
    configure_logging(log_level="DEBUG", json_format=False)

    # Get a logger
    logger = get_logger(__name__)

    # Log some messages
    logger.info("Starting application", version="1.0.0")
    logger.debug("Debug message", extra_data={"key": "value"})

    # Set request ID for tracing
    set_request_id("abc-123")
    logger.info("Processing request", endpoint="/api/test")

    # Clear request ID
    clear_request_id()
    logger.info("Request completed")

    try:
        1 / 0
    except Exception as e:
        logger.error("Division by zero", error=str(e), exc_info=True)
