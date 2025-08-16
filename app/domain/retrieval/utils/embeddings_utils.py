"""Module documentation for `app/domain/retrieval/utils/embeddings_utils.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from app.common.decorators.errors import error_boundary
from app.config import config
from app.constants.errors import GET_CACHED_EMBEDDING

_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """Summary of `get_embedding_model`.

    Args:
        (no arguments)

    Returns:
        SentenceTransformer: Description of return value.

    """
    global _model
    if _model is None:
        _model = SentenceTransformer(config.retrieval.embeddings_model)
    return _model


@lru_cache(maxsize=2048)
@error_boundary(default_return={"error": GET_CACHED_EMBEDDING})
def get_cached_embedding(text: str) -> List[float]:
    """Summary of `get_cached_embedding`.

    Args:
        text (str): Description of text.

    Returns:
        List[float]: Description of return value.

    """
    return get_embedding_model().encode([text])[0].tolist()
