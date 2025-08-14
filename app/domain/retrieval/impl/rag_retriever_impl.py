from __future__ import annotations
from typing import List, Optional
from uuid import uuid4

from llama_index.core import Settings  # if you still want LI for LLM calls
from llama_index.llms.ollama import Ollama

from app.config import CFG
from app.db.repositories.vector_memory_repository import VectorMemoryRepository
from app.domain.embeddings.utils.embeddings_utils import get_cached_embedding  # your cached encoder


class RagRetrieverImpl:
    def __init__(self) -> None:
        self._repo: Optional[VectorMemoryRepository] = None

        # Optional: set global LLM for any LlamaIndex utilities you still use
        Settings.llm = Ollama(
            model=CFG.models.main.model_id,
            temperature=CFG.models.main.temperature,
            context_window=CFG.models.main.max_tokens,
        )

    def _get_repo(self) -> VectorMemoryRepository:
        if self._repo is None:
            self._repo = VectorMemoryRepository(
                path=str(CFG.paths.vector_store_dir),
                collection_name=CFG.memory.collection_name,
                metric="cosine",
            )
        return self._repo

    def retrieve(self, query: str, *, top_k: int = 4) -> List[str]:
        # Compute embedding OUTSIDE repo (repo is storage-only)
        qvec = get_cached_embedding(query)
        results = self._get_repo().similarity_search_by_vector(query_vector=qvec, top_k=top_k)
        return [r["chunk"] for r in results if r.get("chunk")]

    # Optional convenience, if you still want a direct "query"
    def query(self, question: str, *, top_k: int = 4) -> str:
        chunks = self.retrieve(question, top_k=top_k)
        # Keep business logic OUT of the repo: compose an answer here or in a higher service
        return "\n\n".join(chunks[:top_k]) if chunks else ""
