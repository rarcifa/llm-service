import asyncio
import functools
import logging
from typing import Optional, Type, Any, Callable
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

class AppError(Exception):
    """Unified, user-facing application error."""

def error_boundary(
    *,
    map_to: Optional[Type[BaseException]] = AppError,
    default: Any = None,
    reraise: bool = True,
    message: Optional[str] = None,
    log: bool = True,
):
    """Centralized error handling decorator (works for sync & async)."""
    def decorator(fn: Callable):
        logger = logging.getLogger(getattr(fn, "__module__", __name__))

        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await fn(*args, **kwargs)
                except (asyncio.CancelledError, StarletteHTTPException, RequestValidationError):
                    # Preserve cancellation and framework HTTP/validation errors
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
