"""Module documentation for `app/common/utils/strings.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from app.common.decorators.errors import catch_and_log_errors


@catch_and_log_errors(default_return="[truncated]")
def truncate_string(s: str, max_length: int = 200) -> str:
    """Summary of `truncate_string`.

    Args:
        s (str): Description of s.
        max_length (int): Description of max_length, default=200.

    Returns:
        str: Description of return value.

    Raises:
        TypeError: Condition when this is raised.

    """
    if not isinstance(s, str):
        raise TypeError("truncate_string expects a string")
    return s if len(s) <= max_length else s[:max_length] + "..."
