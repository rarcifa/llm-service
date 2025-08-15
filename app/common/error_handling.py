"""Module documentation for `app/common/error_handling.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional, Type

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Summary of `AppError`."""


def error_boundary(
    *,
    map_to: Optional[Type[BaseException]] = AppError,
    default: Any = None,
    reraise: bool = True,
    message: Optional[str] = None,
    log: bool = True,
):
    """Summary of `error_boundary`.

    Args:
        map_to (Optional[Type[BaseException]]): Description of map_to, default=AppError.
        default (Any): Description of default, default=None.
        reraise (bool): Description of reraise, default=True.
        message (Optional[str]): Description of message, default=None.
        log (bool): Description of log, default=True.

    Returns:
        Any: Description of return value.

    Raises:
        map_to: Condition when this is raised.

    """

    def decorator(fn: Callable):
        logger = logging.getLogger(getattr(fn, "__module__", __name__))
        if asyncio.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await fn(*args, **kwargs)
                except (
                    asyncio.CancelledError,
                    StarletteHTTPException,
                    RequestValidationError,
                ):
                    raise
                except Exception as e:
                    if log:
                        logger.exception(message or f"{fn.__name__} failed")
                    if map_to:
                        raise map_to(message or str(e)) from e
                    if reraise:
                        raise
                    return default

            return async_wrapper

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except (StarletteHTTPException, RequestValidationError):
                raise
            except Exception as e:
                if log:
                    logger.exception(message or f"{fn.__name__} failed")
                if map_to:
                    raise map_to(message or str(e)) from e
                if reraise:
                    raise
                return default

        return sync_wrapper

    return decorator


__all__ = ["AppError", "error_boundary"]
