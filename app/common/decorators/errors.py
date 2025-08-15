"""Module documentation for `app/common/decorators/errors.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import functools
import traceback

from app.common.utils.logger import setup_logger

logger = setup_logger()


def catch_and_log_errors(default_return=None):
    """Summary of `catch_and_log_errors`.

    Args:
        default_return: Description of default_return, default=None.

    Returns:
        Any: Description of return value.

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
