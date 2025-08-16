"""Module documentation for `app/domain/memory/impl/pgvector_memory.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from app.common.decorators.errors import error_boundary
from app.common.utils.encoding import sha256
from app.config import config
from app.db.repositories.pgvector_repository import get_pgvector_repo
from app.domain.memory.base.memory_base import MemoryBase
from app.domain.retrieval.utils.embeddings_utils import get_cached_embedding
from app.enums.vector import DistanceMetric


class MemoryImpl(MemoryBase):
    """Summary of `MemoryImpl`.

    Attributes:
        window_size: Description of `window_size`.
    """

    def __init__(self, *, window_size: int = 3) -> None:
        """Summary of `__init__`.

        Args:
            self: Description of self.
            window_size (int): Description of window_size, default=3.

        """
        self.window_size = int(window_size)

    @error_boundary(default_return=None)
    def store_interaction(self, user_input: str, agent_response: str) -> None:
        """Summary of `store_interaction`.

        Args:
            self: Description of self.
            user_input (str): Description of user_input.
            agent_response (str): Description of agent_response.

        """
        text = f"User: {user_input}\nAgent: {agent_response}"
        emb = get_cached_embedding(text)
        with get_pgvector_repo(distance=DistanceMetric.COSINE) as repo:
            repo.upsert(
                collection=config.memory.collection_name,
                embedding=emb,
                document=text,
                metadata={
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "conversation",
                },
                content_sha256=sha256(text),
            )

    @error_boundary(default_return=[])
    def retrieve_context(self, query: str) -> List[str]:
        """Summary of `retrieve_context`.

        Args:
            self: Description of self.
            query (str): Description of query.

        Returns:
            List[str]: Description of return value.

        """
        qemb = get_cached_embedding(query)
        with get_pgvector_repo(distance=DistanceMetric.COSINE) as repo:
            hits = repo.topk(
                query_vec=qemb,
                collection=config.memory.collection_name,
                k=self.window_size,
            )
        return [h["document"] for h in hits if h.get("document")]
