"""
vector_search.py

Provides utilities for vector-based semantic retrieval using ChromaDB.
This module allows querying for top-k most relevant documents based on a user query,
using sentence-transformer embeddings.

Used in RAG (Retrieval-Augmented Generation), memory lookup, or grounding evaluation.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from typing import List

from app.lib.embeddings.chroma import get_chroma_collection
from app.lib.embeddings.embeddings_utils import (
    get_cached_embedding,
    get_embedding_model,
)
from app.lib.utils.decorators.errors import catch_and_log_errors

# === Setup vector collection and embedding model ===
embedding_model = get_embedding_model()
collection = get_chroma_collection()


@catch_and_log_errors(default_return=[])
def retrieve_relevant_docs(query: str, k: int = 3) -> List[str]:
    """
    Retrieves the top-k most relevant documents from the vector store based on semantic similarity.

    Args:
        query (str): The user query to embed and search against.
        k (int, optional): Number of top documents to return. Defaults to 3.

    Returns:
        List[str]: List of retrieved document strings. May be empty on failure.
    """
    embedded_query = get_cached_embedding(query)
    results = collection.query(query_embeddings=[embedded_query], n_results=k)
    docs = results.get("documents", [[]])[0]
    return docs
