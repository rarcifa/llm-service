"""
session_repository.py

Defines standardized error type enums for categorizing session_repository failures.
Used to label and return consistent error codes across agent pipeline components.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from enum import StrEnum


class SessionRepoErrorType(StrEnum):
    """
    Enum representing different categories of agent errors.

    Attributes:
        SESSION_REPO_GET_SESSION_BY_ID: Failed to fetch session by ID.
        SESSION_REPO_CREATE_SESSION: Failed to create a new session.
        SESSION_REPO_GET_OR_CREATE_SESSION: Failed to fetch or create session.
        SESSION_REPO_STORE_MESSAGE: Failed to store a user/agent message.
        SESSION_REPO_GET_MESSAGES: Failed to retrieve message history.
    """

    SESSION_REPO_GET_SESSION_BY_ID = "[session_repository/get_session_by_id] error"
    SESSION_REPO_CREATE_SESSION = "[session_repository/create_session] error"
    SESSION_REPO_GET_OR_CREATE_SESSION = (
        "[session_repository/get_or_create_session] error"
    )
    SESSION_REPO_STORE_MESSAGE = "[session_repository/store_message] error"
    SESSION_REPO_GET_MESSAGES = "[session_repository/get_messages_for_session] error"
