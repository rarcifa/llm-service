"""Module documentation for `app/enums/errors/eval.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from enum import StrEnum


class EvalErrorType(StrEnum):
    """Summary of `EvalErrorType`."""

    SCORE_GROUNDEDNESS = "[eval/score_groundedness_with_embeddings] error"
    SCORE_HELPFULNESS = "[eval/score_helpfulness_with_llm] error"
    COMPUTE_RATING = "[eval/compute_rating] error"
    HALLUCINATION_DETECTION = "[eval/detect_hallucination] error"
    TRACE_SPAN = "[eval/trace_eval_span] error"
    BUILD_DOC_METADATA = "[eval/build_doc_metadata] error"
