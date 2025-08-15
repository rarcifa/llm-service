"""Hallucination risk tagger."""
from __future__ import annotations

from app.domain.eval.utils.eval_utils import detect_hallucination


def filter_hallucinations(
    response: str, retrieved_docs: list[str] | None = None
) -> str:
    docs = retrieved_docs or []
    if not docs:
        return response  # don't warn if we can't assess grounding
    risk = detect_hallucination(response, docs)
    if str(risk).upper() == "HIGH":
        return "[Warning: Potential hallucination detected]\n\n" + response
    return response