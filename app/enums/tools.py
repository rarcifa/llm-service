"""Module documentation for `app/enums/tools.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from enum import StrEnum


class ToolName(StrEnum):
    """Summary of `ToolName`."""

    SEARCH_DOCS = "search_docs"
    PII_REDACTOR = "presidio"
    PROFANITY_FILTER = "profanity_filter"
    PROMPT_INJECTION_DETECTOR = "prompt_injection_detection"
    SUMMARIZE = "summarize"
    CALCULATOR = "calculator"
    HALLUCINATION_BLOCKER = "hallucination_blocker"


class ToolKey(StrEnum):
    """Summary of `ToolKey`."""

    FUNCTION = "function"
    DESCRIPTION = "description"
