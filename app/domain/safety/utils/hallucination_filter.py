"""Module documentation for `app/domain/safety/utils/hallucination_filter.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from app.common.decorators.errors import error_boundary
from app.constants.errors import FILTER_HALLUCINATIONS
from app.domain.eval.utils.eval_utils import detect_hallucination


@error_boundary(default_return={"error": FILTER_HALLUCINATIONS})
def filter_hallucinations(
    response: str, retrieved_docs: list[str] | None = None
) -> str:
    """Summary of `filter_hallucinations`.

    Args:
        response (str): Description of response.
        retrieved_docs (list[str] | None): Description of retrieved_docs, default=None.

    Returns:
        str: Description of return value.

    """
    docs = retrieved_docs or []
    if not docs:
        return response
    risk = detect_hallucination(response, docs)
    if str(risk).upper() == "HIGH":
        return "[Warning: Potential hallucination detected]\n\n" + response
    return response
