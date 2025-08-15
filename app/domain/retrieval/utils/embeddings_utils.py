"""Utility functions for sentence embedding models and cached encodes."""
from __future__ import annotations


from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from app.config import CFG

# Lazily initialized singleton model
_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """Return a lazily initialized embedding model instance.

    Returns:
        The loaded SentenceTransformer model.
    """
    global _model
    if _model is None:
        # Read embedding model from CFG.retrieval.embeddings_model
        _model = SentenceTransformer(CFG.retrieval.embeddings_model)
    return _model


@lru_cache(maxsize=2048)
def get_cached_embedding(text: str) -> List[float]:
    """Return a cached embedding vector for the given text.

    Args:
        text: Input string to embed.

    Returns:
        Embedding as a list of floats.
    """
    # encode returns a numpy array; convert to list for JSON/serialization friendliness
    return get_embedding_model().encode([text])[0].tolist()