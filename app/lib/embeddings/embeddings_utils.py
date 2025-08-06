"""
embeddings_utils.py

Provides functions to load and cache sentence embedding models using
`sentence-transformers`. Supports lazy initialization and efficient
embedding retrieval with LRU caching.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

# === Lazy-loaded singleton model instance ===
_model = None


def get_embedding_model() -> SentenceTransformer:
    """
    Lazily initializes and returns the sentence embedding model.

    Returns:
        SentenceTransformer: The loaded embedding model instance.
    """
    from app.config import embedding_model

    global _model
    if _model is None:
        _model = SentenceTransformer(embedding_model)
    return _model


@lru_cache(maxsize=2048)
def get_cached_embedding(text: str) -> list[float]:
    """
    Generates a cached sentence embedding for a given input text.

    Args:
        text (str): The text string to embed.

    Returns:
        list[float]: The embedding vector as a list of floats.
    """
    return get_embedding_model().encode([text])[0].tolist()
