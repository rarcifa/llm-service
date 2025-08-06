"""
string_utils.py

Utility function for safely truncating long strings with optional length limits.
Includes error handling and fallback behavior.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from app.lib.utils.decorators.errors import catch_and_log_errors


@catch_and_log_errors(default_return="[truncated]")
def truncate_string(s: str, max_length: int = 200) -> str:
    """
    Truncates a string to a maximum length and appends '...' if it's too long.

    Args:
        s (str): The input string to truncate.
        max_length (int, optional): Maximum allowed length. Defaults to 200.

    Returns:
        str: The truncated string, or the original if within limit.

    Raises:
        TypeError: If `s` is not a string.
    """
    if not isinstance(s, str):
        raise TypeError("truncate_string expects a string")

    return s if len(s) <= max_length else s[:max_length] + "..."
