"""Module documentation for `app/domain/safety/utils/injection_detector.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Iterable

from app.common.decorators.errors import catch_and_log_errors
from app.common.utils.logger import setup_logger

logger = setup_logger()


@lru_cache(maxsize=1)
def _compiled_injection_regexes():
    """Summary of `_compiled_injection_regexes`.

    Args:
        (no arguments)

    Returns:
        Any: Description of return value.

    """
    patterns: Iterable[str] = [
        "(?i)\\b(ignore|bypass|override)\\b.*\\b(system|instruction)s?\\b",
        "(?i)\\b(disable|turn\\s*off)\\b.*\\b(guardrails|safety)\\b",
        "(?i)\\b(api[_-]?key|password|secret)\\b\\s*[:=]\\s*\\S+",
    ]
    compiled = []
    for p in patterns:
        try:
            compiled.append(re.compile(p, flags=re.IGNORECASE))
        except re.error as e:
            logger.warning("Skipping bad injection regex", pattern=p, error=str(e))
    return tuple(compiled)


@catch_and_log_errors(default_return=False)
def detect_prompt_injection(text: str) -> bool:
    """Summary of `detect_prompt_injection`.

    Args:
        text (str): Description of text.

    Returns:
        bool: Description of return value.

    """
    if not isinstance(text, str):
        return False
    for rx in _compiled_injection_regexes():
        if rx.search(text):
            return True
    return False
