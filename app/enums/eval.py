"""
eval.py

Defines enums related to evaluation configuration, scoring categories,
and result keys for automated agent evaluation (e.g., grounding, helpfulness, hallucination).

These enums standardize the internal and external references to evaluation statuses and metadata,
used throughout the eval pipeline and observability layers.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from enum import StrEnum


class EvalConfigKey(StrEnum):
    """
    Keys to toggle evaluation-related behaviors in config.

    Attributes:
        ENABLED: Evaluation is enabled.
        DISABLED: Evaluation is disabled.
    """

    ENABLED = "enabled"
    DISABLED = "disabled"


class RetrievalConfigKey(StrEnum):
    """
    Keys to toggle document retrieval for evaluation.

    Attributes:
        ENABLED: Retrieval is enabled.
        DISABLED: Retrieval is disabled.
    """

    ENABLED = "enabled"
    DISABLED = "disabled"


class EvalKey(StrEnum):
    """
    Top-level keys used to categorize evaluation results and span-level tracing
    for agent evaluation metrics and document retrieval.

    Attributes:
        AGENT: Key for the overall agent evaluation span.
        GROUNDING: Key for the grounding evaluation result.
        DOCS: Key used to log the full list of retrieved documents.
        PREVIEW: Key used to log a preview of top-k retrieved chunks.
    """

    AGENT = "agent.eval"
    GROUNDING = "eval.grounding"
    DOCS = "retrieval.docs"
    PREVIEW = "retrieval.docs_preview"


class GroundingKey(StrEnum):
    """
    Outcome of grounding evaluation (does response match context?).

    Attributes:
        PASS: The response is grounded in context.
        FAIL: The response is not grounded in context.
    """

    PASS = "grounding_pass"
    FAIL = "grounding_fail"


class HelpfulnessKey(StrEnum):
    """
    Outcome of helpfulness evaluation (is the response useful?).

    Attributes:
        PASS: The response is helpful.
        FAIL: The response is not helpful.
    """

    PASS = "helpfulness_pass"
    FAIL = "helpfulness_fail"


class RatingKey(StrEnum):
    """
    General 3-point rating scale for human/automated feedback.

    Attributes:
        PASS: Positive outcome.
        FAIL: Negative outcome.
        NEUTRAL: Neither positive nor negative.
    """

    PASS = "pass"
    FAIL = "fail"
    NEUTRAL = "neutral"


class HallucinationKey(StrEnum):
    """
    Degree of hallucination detected in the response.

    Attributes:
        LOW: Low risk of hallucination.
        MEDIUM: Moderate hallucination detected.
        HIGH: High hallucination detected.
        UNKNOWN: No classification available.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class TraceMetaKey(StrEnum):
    """
    Enum of standardized metadata keys for OpenTelemetry span attributes
    and evaluation trace logging. Ensures consistent naming across spans.

    General Trace Info:
        TRACE_ID: Unique trace ID for the evaluation span.
        TRACE_TIMESTAMP: ISO timestamp of when the span was created.

    Identifiers:
        RESPONSE_ID: ID of the agent response being evaluated.
        MESSAGE_ID: ID of the user message.
        SESSION_ID: Session-level identifier.

    Prompt Metadata:
        PROMPT_VERSION: Prompt version identifier (semantic or hash).
        PROMPT_TEMPLATE_NAME: Name of the template used (e.g., 'qa').
        PROMPT_SYSTEM_PROMPT: Raw system-level prompt string.
        PROMPT_RENDERED_PREVIEW: Rendered prompt preview (may be truncated).
        PROMPT_RENDERED_TOKENS: Token count of the rendered prompt.
        PROMPT_TEMPLATE_TOKENS: Token count of the template string.

    Input Metadata:
        INPUT_RAW: User input before any filtering or sanitization.
        INPUT_FILTERED: Cleaned/normalized version of the input.
        INPUT_LENGTH: Length of input string.

    Output Metadata:
        OUTPUT_RESPONSE: Raw model response.
        OUTPUT_RESPONSE_LENGTH: Length of the model's response.

    Retrieval Metadata:
        RETRIEVAL_DOCS_COUNT: Number of retrieved documents used as context.
        RETRIEVAL_TOP_CHUNK: Top-ranked document chunk (truncated).
        RETRIEVAL_TOP_SCORE: Similarity score of the top-ranked chunk.
        RETRIEVAL_TOP_SOURCE: Source of the top-ranked chunk (e.g., memory, vector).
    """

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
    """
    Enum for identifying the source of a retrieved document.

    Attributes:
        MEMORY: Chunk was retrieved from in-session memory (e.g., dialogue).
        VECTOR: Chunk was retrieved from vector store (e.g., RAG search).
    """

    MEMORY = "memory"
    VECTOR = "vector"


class EvalResultKey(StrEnum):
    """
    Keys used in the final evaluation result dictionary.

    Attributes:
        RATING: Final classification (e.g., 'pass', 'fail', 'neutral').
        HELPFULNESS: LLM-as-a-judge or rule-based helpfulness score/output.
        GROUNDING: Cosine similarity or grounding metric between response and context.
        HALLUCINATION: Degree of hallucination risk (e.g., low/medium/high).
    """

    RATING = "rating"
    HELPFULNESS = "helpfulness"
    GROUNDING = "grounding_score"
    HALLUCINATION = "hallucination_risk"


class RetrievalDocKey(StrEnum):
    """
    Keys used for representing metadata of each retrieved document chunk.

    Attributes:
        CHUNK: Truncated document text or preview snippet.
        SCORE: Similarity score (e.g., cosine similarity to the query).
        SOURCE: Source type (e.g., 'memory' or 'vector').
    """

    CHUNK = "chunk"
    SCORE = "score"
    SOURCE = "source"
