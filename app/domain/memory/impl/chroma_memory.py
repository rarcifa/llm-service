from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List

from app.common.decorators.errors import catch_and_log_errors
from app.db.repositories.vector_memory_repository import VectorMemoryRepository
from app.domain.embeddings.utils.embeddings_utils import get_cached_embedding
from app.domain.memory.base.memory_base import MemoryBase

class MemoryImpl(MemoryBase):
    """Semantic memory backed by VectorMemoryRepository (DI only)."""

    def __init__(self, *, repo: VectorMemoryRepository, window_size: int = 3) -> None:
        self.repo = repo
        self.window_size = int(window_size)

    @catch_and_log_errors(default_return=None)
    def store_interaction(self, user_input: str, agent_response: str) -> None:
        combined = f"User: {user_input}\nAgent: {agent_response}"
        emb = get_cached_embedding(combined)
        self.repo.upsert_vectors(
            ids=[str(uuid.uuid4())],
            embeddings=[emb],
            documents=[combined],
            metadatas=[{"timestamp": datetime.now(timezone.utc).isoformat()}],
        )

    @catch_and_log_errors(default_return=[])
    def retrieve_context(self, query: str) -> List[str]:
        qemb = get_cached_embedding(query)
        results = self.repo.similarity_search_by_vector(query_vector=qemb, top_k=self.window_size)
        return [r["chunk"] for r in results if r.get("chunk")]
