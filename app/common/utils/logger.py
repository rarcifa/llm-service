"""
logger.py

Configures a structured logger using `structlog`, with dynamic settings based on
environment (`dev`, `prod`, etc.) and log level.

In development:
- Logs are human-readable with timestamps.
In production:
- Logs are JSON-formatted for ingestion by centralized log systems.
- Noise from common libraries (Presidio, Transformers, etc.) is suppressed.

This logger is used across the entire application and is safe to call multiple times.

Environment Variables:
- LOG_LEVEL: The minimum log level (e.g., INFO, DEBUG).
- ENV: The environment name ("dev", "prod", etc.).

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import logging
import os
import sys
import warnings
from typing import Any

import structlog

# Load environment settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ENV = os.getenv("ENV", "dev").lower()


def setup_logger(env: str = "dev", log_level: str = "INFO") -> Any:
    """
    Sets up and returns a structured logger using structlog.

    Args:
        env (str): The environment name ("dev" or "prod"). Defaults to "dev".
        log_level (str): Logging level (e.g., "INFO", "DEBUG"). Defaults to "INFO".

    Returns:
        structlog.stdlib.BoundLogger: A structured logger instance.
    """
    # Suppress tokenizer and ChromaDB noise
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("CHROMA_TELEMETRY_ENABLED", "false")

    # Configure standard Python logging for compatibility
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Suppress unwanted library warnings in production
    if env == "prod":
        warnings.filterwarnings("ignore", category=FutureWarning)
        warnings.filterwarnings("ignore", category=UserWarning)

        logging.getLogger("presidio").setLevel(logging.ERROR)
        logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)
        logging.getLogger("presidio-anonymizer").setLevel(logging.ERROR)
        logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
        logging.getLogger("transformers").setLevel(logging.ERROR)
        logging.getLogger("chromadb").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Define processors for structlog pipeline
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Renderer based on environment
    if env == "dev":
        processors += [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        processors += [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]

    # Final logger configuration
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()
