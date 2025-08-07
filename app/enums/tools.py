"""
tools.py

Defines enums related to tool names and tool metadata keys used in the dynamic
tool registry for the agent framework. These tools include document search,
PII redaction, and profanity filtering.

Used to register and access tool functions and metadata consistently across
the system via `ToolName` and `ToolKey`.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from enum import StrEnum


class ToolName(StrEnum):
    """
    Enum of tool identifiers used in the system.

    Attributes:
        SEARCH_DOCS: Tool for vector-based document search or RAG.
        PII_REDACTOR: Tool that redacts personally identifiable information.
        PROFANITY_FILTER: Tool that removes or sanitizes offensive language.
    """

    SEARCH_DOCS = "search_docs"
    PII_REDACTOR = "presidio"
    PROFANITY_FILTER = "profanity_filter"
    PROMPT_INJECTION_DETECTOR = "prompt_injection_detection"
    SUMMARIZE = "summarize"
    CALCULATOR = "calculator"
    HALLUCINATION_BLOCKER = "hallucination_blocker"


class ToolKey(StrEnum):
    """
    Enum of metadata keys used to access tool components in the registry.

    Attributes:
        FUNCTION: Key to access the callable function.
        DESCRIPTION: Key to access the human-readable description of the tool.
    """

    FUNCTION = "function"
    DESCRIPTION = "description"
