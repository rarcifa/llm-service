"""
retry.py

Defines a reusable `with_retry` decorator for retrying a function on failure.
Supports exponential backoff and configurable retry limits.

This is useful for wrapping external service calls (e.g., LLMs, DBs, HTTP)
that may intermittently fail and benefit from retry logic.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import logging
import time

logger = logging.getLogger(__name__)


def with_retry(max_retries: int = 3, backoff_factor: float = 1.5):
    """
    Decorator that retries a function on exception using exponential backoff.

    Args:
        max_retries (int): Maximum number of attempts before failing.
        backoff_factor (float): Multiplier for the delay between retries.

    Returns:
        Callable: Wrapped function with retry logic.

    Raises:
        RuntimeError: If all retry attempts fail.

    Example:
        @with_retry(max_retries=5, backoff_factor=2)
        def call_api(): ...
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            delay = 1
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Retry #{retries + 1} failed: {e}")
                    time.sleep(delay)
                    delay *= backoff_factor
                    retries += 1
            raise RuntimeError(
                f"Function {func.__name__} failed after {max_retries} retries"
            )

        return wrapper

    return decorator
