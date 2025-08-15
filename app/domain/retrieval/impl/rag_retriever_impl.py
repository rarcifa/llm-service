"""Module documentation for `app/domain/retrieval/impl/rag_retriever_impl.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from typing import List

from app.config import config
from app.db.repositories.pgvector_repository import get_pgvector_repo
from app.domain.retrieval.utils.embeddings_utils import get_cached_embedding


class RagRetrieverImpl:
    """Summary of `RagRetrieverImpl`."""

    def retrieve(self, query: str, *, top_k: int = 4) -> List[str]:
        """Summary of `retrieve`.

        Args:
            self: Description of self.
            query (str): Description of query.
            top_k (int): Description of top_k, default=4.

        Returns:
            List[str]: Description of return value.

        """
        qvec = get_cached_embedding(query)
        with get_pgvector_repo(distance="cosine") as repo:
            hits = repo.topk(
                query_vec=qvec, collection=config.memory.collection_name, k=top_k
            )
        return [h["document"] for h in hits if h.get("document")]

    def query(self, question: str, *, top_k: int = 4) -> str:
        """Summary of `query`.

        Args:
            self: Description of self.
            question (str): Description of question.
            top_k (int): Description of top_k, default=4.

        Returns:
            str: Description of return value.

        """
        chunks = self.retrieve(question, top_k=top_k)
        return "\n\n".join(chunks[:top_k]) if chunks else ""
