"""Module documentation for `app/common/utils/logger.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import logging
import os
import sys
import warnings
from typing import Any

import structlog

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ENV = os.getenv("ENV", "dev").lower()


def setup_logger(env: str = "dev", log_level: str = "INFO") -> Any:
    """Summary of `setup_logger`.

    Args:
        env (str): Description of env, default='dev'.
        log_level (str): Description of log_level, default='INFO'.

    Returns:
        Any: Description of return value.

    """
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("CHROMA_TELEMETRY_ENABLED", "false")
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level)
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
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
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
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()
