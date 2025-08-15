"""Persistence helpers for agent conversations (impl layer)."""
from __future__ import annotations


import hashlib
import uuid
from typing import Optional

from app.config import CFG
from app.db.repositories.pgvector_repository import get_pgvector_repo
from app.db.repositories.session_repository import get_session_repo
from app.domain.retrieval.utils.embeddings_utils import get_cached_embedding
from app.enums.prompts import RoleKey


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def persist_conversation(
    *,
    session_id: str,
    user_input: str,
    response: str,
    tokens_used: Optional[int] = None,
    metadata: Optional[dict] = None,
) -> None:
    """Persist the user/agent conversation to Postgres (relational + pgvector)."""
    # 1) Relational history
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

    # 2) Vector index (pgvector)
    emb = get_cached_embedding(response)
    with get_pgvector_repo(distance="cosine") as vrepo:
        vrepo.upsert(
            session_id=session_id,
            collection=CFG.memory.collection_name,
            embedding=emb,
            document=response,
            metadata={"session_id": session_id, **(metadata or {})},
            content_sha256=_sha256(response),
        )