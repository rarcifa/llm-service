"""Module documentation for `app/enums/prompts.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from enum import StrEnum


class ModelType(StrEnum):
    """Summary of `ModelType`."""

    LLAMA3 = "llama3"


class ScoreKey(StrEnum):
    """Summary of `ScoreKey`."""

    HELPFULNESS = "eval.helpfulness"
    GROUNDING = "eval.grounding_score"
    HALLUCINATION = "eval.hallucination_risk"
    RATING = "eval.rating"


class JsonKey(StrEnum):
    """Summary of `JsonKey`."""

    SESSION_ID = "session_id"
    RESPONSE_ID = "response_id"
    TRACE_ID = "trace_id"
    FEEDBACK_ID = "feedback_id"
    MESSAGE_ID = "message_id"
    RATING = "rating"
    STATUS = "status"
    INPUT = "input"
    RESPONSE = "response"


class PromptConfigKey(StrEnum):
    """Summary of `PromptConfigKey`."""

    TEMPLATE = "template"
    TEMPLATE_NAME = "template_name"
    VERSION = "version"
    NAME = "name"
    ID = "id"


class RoleKey(StrEnum):
    """Summary of `RoleKey`."""

    USER = "user"
    AGENT = "agent"
