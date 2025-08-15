"""Module documentation for `app/enums/errors/session_repository.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from enum import StrEnum


class SessionRepoErrorType(StrEnum):
    """Summary of `SessionRepoErrorType`."""

    SESSION_REPO_GET_SESSION_BY_ID = "[session_repository/get_session_by_id] error"
    SESSION_REPO_CREATE_SESSION = "[session_repository/create_session] error"
    SESSION_REPO_GET_OR_CREATE_SESSION = (
        "[session_repository/get_or_create_session] error"
    )
    SESSION_REPO_STORE_MESSAGE = "[session_repository/store_message] error"
    SESSION_REPO_GET_MESSAGES = "[session_repository/get_messages_for_session] error"
