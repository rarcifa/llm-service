"""
eval.py

Defines EvalErrorType enum used to categorize and trace errors
that occur during evaluation steps such as grounding scoring,
helpfulness judging, hallucination detection, and final rating.

This improves observability, logging, and debugging when
integrated with error decorators and tracing.

Author: Ricardo Arcifa
Created: 2025-08-06
"""

from enum import StrEnum


class EvalErrorType(StrEnum):
    """
    Enum representing evaluation-related error categories.

    Attributes:
        SCORE_GROUNDEDNESS (str): Error during embedding-based grounding calculation.
        SCORE_HELPFULNESS (str): Error from LLM-based helpfulness scoring.
        COMPUTE_RATING (str): Error while computing pass/fail rating.
        HALLUCINATION_DETECTION (str): Error in overlap-based hallucination detection.
        TRACE_SPAN (str): Error during OpenTelemetry span tagging.
        BUILD_DOC_METADATA (str): Error building document metadata for eval trace.
    """

    SCORE_GROUNDEDNESS = "[eval/score_groundedness_with_embeddings] error"
    SCORE_HELPFULNESS = "[eval/score_helpfulness_with_llm] error"
    COMPUTE_RATING = "[eval/compute_rating] error"
    HALLUCINATION_DETECTION = "[eval/detect_hallucination] error"
    TRACE_SPAN = "[eval/trace_eval_span] error"
    BUILD_DOC_METADATA = "[eval/build_doc_metadata] error"
