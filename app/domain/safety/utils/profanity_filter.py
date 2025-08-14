# app/domain/safety/utils/profanity_filter.py
"""Simple profanity masking (manifest-driven)."""
from __future__ import annotations
import re
from functools import lru_cache
from app.common.decorators.errors import catch_and_log_errors

def _censor(word: str) -> str:
    return word[0] + "*" * (len(word) - 2) + word[-1] if len(word) > 2 else "*" * len(word)

@lru_cache(maxsize=1)
def _profanity_regex():
    # Late import to avoid cycles
    from app.config import CFG
    words = tuple(CFG.guardrails.input_profanity_list or ())
    if not words:
        # Match nothing
        return re.compile(r"(?!x)x")
    escaped = [re.escape(w) for w in words]
    return re.compile(r"\b(" + "|".join(escaped) + r")\b", flags=re.IGNORECASE)

@catch_and_log_errors(default_return="[PROFANITY FILTER FAILED]")
def filter_profanity(text: str) -> str:
    """Mask profane words with asterisks, preserving first/last char."""
    rx = _profanity_regex()
    return rx.sub(lambda m: _censor(m.group()), text)
