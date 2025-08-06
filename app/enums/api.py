"""
api.py

Defines enums used for request/response key names in API payloads and
standard HTTP status codes used throughout the application.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from enum import IntEnum, StrEnum


class RequestKey(StrEnum):
    """
    Enum for expected request payload keys.

    Attributes:
        INPUT: The user's input text for the agent.
        SESSION_ID: Identifier for the session (used for continuity).
    """

    INPUT = "input"
    SESSION_ID = "session_id"


class ResponseKey(StrEnum):
    """
    Enum for keys used in the response payloads returned by the agent or API.

    Attributes:
        ERROR: Key for the error message or type.
        RESPONSE: The agent's generated response text.
        PROMPT: The final rendered prompt (for debugging or tracing).
        STREAM: Streaming mode indicator or stream object.
    """

    ERROR = "error"
    RESPONSE = "response"
    PROMPT = "prompt"
    STREAM = "stream"


class HTTPStatusCode(IntEnum):
    """
    Enum for HTTP status codes used in API responses.

    Success:
        OK (200): Request succeeded.
        CREATED (201): Resource successfully created.
        ACCEPTED (202): Request accepted for processing.
        NO_CONTENT (204): Request succeeded with no response body.

    Client Errors:
        BAD_REQUEST (400): Malformed or invalid request.
        UNAUTHORIZED (401): Authentication required.
        FORBIDDEN (403): Request not allowed.
        NOT_FOUND (404): Resource not found.
        CONFLICT (409): Request conflicts with current state.
        UNPROCESSABLE_ENTITY (422): Validation or semantic error in request.

    Server Errors:
        INTERNAL_SERVER_ERROR (500): Unexpected server error.
        NOT_IMPLEMENTED (501): API method not implemented.
        BAD_GATEWAY (502): Upstream service failed.
        SERVICE_UNAVAILABLE (503): Service temporarily unavailable.
    """

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
