"""Module documentation for `app/enums/api.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from enum import IntEnum, StrEnum


class RequestKey(StrEnum):
    """Summary of `RequestKey`."""

    INPUT = "input"
    SESSION_ID = "session_id"


class ResponseKey(StrEnum):
    """Summary of `ResponseKey`."""

    ERROR = "error"
    RESPONSE = "response"
    PROMPT = "prompt"
    STREAM = "stream"


class HTTPStatusCode(IntEnum):
    """Summary of `HTTPStatusCode`."""

    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
