"""Module documentation for `app/common/decorators/retry.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import logging
import time

logger = logging.getLogger(__name__)


def with_retry(max_retries: int = 3, backoff_factor: float = 1.5):
    """Summary of `with_retry`.

    Args:
        max_retries (int): Description of max_retries, default=3.
        backoff_factor (float): Description of backoff_factor, default=1.5.

    Returns:
        Any: Description of return value.

    Raises:
        RuntimeError: Condition when this is raised.

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
