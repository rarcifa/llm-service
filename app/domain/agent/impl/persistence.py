"""Persistence helpers for agent conversations (impl layer)."""

from __future__ import annotations

import uuid
from typing import Optional

from app.config import CFG, Paths
from app.db.repositories.session_repository import get_session_repo
from app.db.repositories.vector_memory_repository import VectorMemoryRepository
from app.domain.embeddings.impl.embeddings_impl import EmbeddingsImpl
from app.domain.embeddings.utils.embeddings_utils import get_cached_embedding
from app.domain.memory.impl.chroma_memory import MemoryImpl
from app.enums.prompts import RoleKey

def persist_conversation(
    *,
    session_id: str,
    user_input: str,
    response: str,
    tokens_used: Optional[int] = None,
    metadata: Optional[dict] = None,
) -> None:
    """Persist the user/agent conversation to DB and semantic memory."""
    with get_session_repo() as repo:
        repo.get_or_create_session(session_id)
        repo.store_message(
            session_id=session_id,
            role=RoleKey.USER,
            content=user_input,
            message_id=str(uuid.uuid4()),
            tokens_used=tokens_used,
            metadata=metadata,
        )
        repo.store_message(
            session_id=session_id,
            role=RoleKey.AGENT,
            content=response.strip(),
            message_id=str(uuid.uuid4()),
            tokens_used=tokens_used,
            metadata=metadata,
        )

    # 2) Vector index (Chroma) — storage-only via repo
    vrepo = VectorMemoryRepository(
        path=str(CFG.paths.vector_store_dir),
        collection_name=CFG.memory.collection_name,
    )
    emb = get_cached_embedding(response)
    vrepo.upsert_vectors(
        ids=[str(uuid.uuid4())],
        embeddings=[emb],
        documents=[response],
        metadatas=[{"session_id": session_id, **(metadata or {})}],
    )
