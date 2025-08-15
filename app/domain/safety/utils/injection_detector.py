"""Pattern-based prompt-injection detection (manifest-driven)."""
from __future__ import annotations

import re
from functools import lru_cache

from app.common.decorators.errors import catch_and_log_errors


@lru_cache(maxsize=1)
def _compiled_injection_regexes():
    # Late import to avoid cycles
    from app.config import CFG

    patterns = CFG.guardrails.input_prompt_injection_patterns or ()
    return tuple(re.compile(p, flags=re.IGNORECASE) for p in patterns)


@catch_and_log_errors(default_return=False)
def detect_prompt_injection(text: str) -> bool:
    """Return True if a known injection pattern is present in `text`."""
    for rx in _compiled_injection_regexes():
        if rx.search(text):
            return True
    return False