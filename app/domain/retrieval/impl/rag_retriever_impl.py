from __future__ import annotations

from typing import List

from app.config import CFG
from app.db.repositories.pgvector_repository import get_pgvector_repo
from app.domain.retrieval.utils.embeddings_utils import get_cached_embedding


class RagRetrieverImpl:
    """RAG retriever backed by Postgres + pgvector."""

    def retrieve(self, query: str, *, top_k: int = 4) -> List[str]:
        qvec = get_cached_embedding(query)
        with get_pgvector_repo(distance="cosine") as repo:
            hits = repo.topk(
                query_vec=qvec, collection=CFG.memory.collection_name, k=top_k
            )
        return [h["document"] for h in hits if h.get("document")]

    def query(self, question: str, *, top_k: int = 4) -> str:
        chunks = self.retrieve(question, top_k=top_k)
        return "\n\n".join(chunks[:top_k]) if chunks else ""
