from __future__ import annotations

import re
from functools import lru_cache
from typing import Iterable

from app.common.decorators.errors import catch_and_log_errors
from app.common.utils.logger import setup_logger

logger = setup_logger()

@lru_cache(maxsize=1)
def _compiled_injection_regexes():
    # Late import to avoid cycles
    from app.config import CFG

    patterns: Iterable[str] = [
        r"(?i)\b(ignore|bypass|override)\b.*\b(system|instruction)s?\b",
        r"(?i)\b(disable|turn\s*off)\b.*\b(guardrails|safety)\b",
        r"(?i)\b(api[_-]?key|password|secret)\b\s*[:=]\s*\S+",
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
    """Return True if a known injection pattern is present in `text`."""
    # Defensive: only operate on strings
    if not isinstance(text, str):
        return False
    for rx in _compiled_injection_regexes():
        if rx.search(text):
            return True
    return False
