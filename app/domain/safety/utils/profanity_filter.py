"""Module documentation for `app/domain/safety/utils/profanity_filter.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

import re
from functools import lru_cache

from app.common.decorators.errors import error_boundary


def _censor(word: str) -> str:
    """Summary of `_censor`.

    Args:
        word (str): Description of word.

    Returns:
        str: Description of return value.

    """
    return (
        word[0] + "*" * (len(word) - 2) + word[-1] if len(word) > 2 else "*" * len(word)
    )


@lru_cache(maxsize=1)
def _profanity_regex():
    """Summary of `_profanity_regex`.

    Args:
        (no arguments)

    Returns:
        Any: Description of return value.

    """
    words = tuple(["damn", "hell", "shit", "fuck"])
    if not words:
        return re.compile("(?!x)x")
    escaped = [re.escape(w) for w in words]
    return re.compile("\\b(" + "|".join(escaped) + ")\\b", flags=re.IGNORECASE)


@error_boundary(default_return="[PROFANITY FILTER FAILED]")
def filter_profanity(text: str) -> str:
    """Summary of `filter_profanity`.

    Args:
        text (str): Description of text.

    Returns:
        str: Description of return value.

    """
    rx = _profanity_regex()
    return rx.sub(lambda m: _censor(m.group()), text)
