"""Retriever contract (base).

Author: Ricardo Arcifa
Created: 2025-08-07
"""
from __future__ import annotations


from abc import ABC, abstractmethod
from typing import List


class RetrieverBase(ABC):
    """Abstract interface for retrieval-augmented lookups."""

    @abstractmethod
    def retrieve(self, query: str, *, top_k: int = 4) -> List[str]:
        """Return the top-k relevant context chunks for `query` (no generation)."""
        raise NotImplementedError

    @abstractmethod
    def query(self, question: str, *, top_k: int = 4) -> str:
        """Return a model-formatted answer using RAG over the vector store."""
        raise NotImplementedError