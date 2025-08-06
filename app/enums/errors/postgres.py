"""
postgres.py

Defines standardized error type enums for categorizing postgres failures.
Used to label and return consistent error codes across agent pipeline components.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from enum import StrEnum


class PostgresErrorType(StrEnum):
    """
    Enum representing different categories of agent errors.

    Attributes:
        POSTGRES_INIT_DB: Failure during DB initialization.
    """

    POSTGRES_INIT_DB = "[postgres/init_db] error"
