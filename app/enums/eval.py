"""Module documentation for `app/enums/eval.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from enum import StrEnum


class EvalConfigKey(StrEnum):
    """Summary of `EvalConfigKey`."""

    ENABLED = "enabled"
    DISABLED = "disabled"


class RetrievalConfigKey(StrEnum):
    """Summary of `RetrievalConfigKey`."""

    ENABLED = "enabled"
    DISABLED = "disabled"


class EvalKey(StrEnum):
    """Summary of `EvalKey`."""

    AGENT = "agent.eval"
    GROUNDING = "eval.grounding"
    DOCS = "retrieval.docs"
    PREVIEW = "retrieval.docs_preview"


class GroundingKey(StrEnum):
    """Summary of `GroundingKey`."""

    PASS = "grounding_pass"
    FAIL = "grounding_fail"


class HelpfulnessKey(StrEnum):
    """Summary of `HelpfulnessKey`."""

    PASS = "helpfulness_pass"
    FAIL = "helpfulness_fail"


class RatingKey(StrEnum):
    """Summary of `RatingKey`."""

    PASS = "pass"
    FAIL = "fail"
    NEUTRAL = "neutral"


class HallucinationKey(StrEnum):
    """Summary of `HallucinationKey`."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class TraceMetaKey(StrEnum):
    """Summary of `TraceMetaKey`."""

    TRACE_ID = "trace.id"
    TRACE_TIMESTAMP = "trace.timestamp"
    RESPONSE_ID = "response.id"
    MESSAGE_ID = "message.id"
    SESSION_ID = "session.id"
    PROMPT_VERSION = "prompt.version"
    PROMPT_TEMPLATE_NAME = "prompt.template_name"
    PROMPT_SYSTEM_PROMPT = "prompt.system_prompt"
    PROMPT_RENDERED_PREVIEW = "prompt.rendered_preview"
    PROMPT_RENDERED_TOKENS = "prompt.rendered_tokens"
    PROMPT_TEMPLATE_TOKENS = "prompt.template_tokens"
    INPUT_RAW = "input.raw"
    INPUT_FILTERED = "input.filtered"
    INPUT_LENGTH = "input.length"
    OUTPUT_RESPONSE = "output.response"
    OUTPUT_RESPONSE_LENGTH = "output.response_length"
    RETRIEVAL_DOCS_COUNT = "retrieval.docs_count"
    RETRIEVAL_TOP_CHUNK = "retrieval.top_chunk"
    RETRIEVAL_TOP_SCORE = "retrieval.top_score"
    RETRIEVAL_TOP_SOURCE = "retrieval.top_source"


class RetrievalSource(StrEnum):
    """Summary of `RetrievalSource`."""

    MEMORY = "memory"
    VECTOR = "vector"


class EvalResultKey(StrEnum):
    """Summary of `EvalResultKey`."""

    RATING = "rating"
    HELPFULNESS = "helpfulness"
    GROUNDING = "grounding_score"
    HALLUCINATION = "hallucination_risk"


class RetrievalDocKey(StrEnum):
    """Summary of `RetrievalDocKey`."""

    CHUNK = "chunk"
    SCORE = "score"
    SOURCE = "source"
