"""
error_handling.py

Defines a reusable decorator `catch_and_log_errors` that wraps a function to
safely catch exceptions, log them with traceback, and return a fallback value.

Used to harden functions against unexpected runtime errors, particularly in
non-critical paths like analytics, monitoring, or optional computations.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import functools
import traceback

from app.lib.utils.logger import setup_logger

logger = setup_logger()


def catch_and_log_errors(default_return=None):
    """
    Decorator that catches any unhandled exceptions in a function, logs the error,
    and safely returns a fallback value instead of raising the exception.

    Args:
        default_return (Any, optional): The value to return if an exception occurs.
            Defaults to None.

    Returns:
        Callable: Wrapped function with exception handling.

    Example:
        @catch_and_log_errors(default_return=[])
        def load_data(): ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in {func.__name__}",
                    error=str(e),
                    traceback=traceback.format_exc(),
                )
                return default_return

        return wrapper

    return decorator
