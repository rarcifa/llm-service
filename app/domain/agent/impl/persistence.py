"""Module documentation for `app/domain/agent/impl/persistence.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Optional

from app.config import config
from app.db.repositories.pgvector_repository import get_pgvector_repo
from app.db.repositories.session_repository import get_session_repo
from app.domain.retrieval.utils.embeddings_utils import get_cached_embedding
from app.enums.prompts import RoleKey


def _sha256(s: str) -> str:
    """Summary of `_sha256`.

    Args:
        s (str): Description of s.

    Returns:
        str: Description of return value.

    """
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def persist_conversation(
    *,
    session_id: str,
    user_input: str,
    response: str,
    tokens_used: Optional[int] = None,
    metadata: Optional[dict] = None,
) -> None:
    """Summary of `persist_conversation`.

    Args:
        session_id (str): Description of session_id.
        user_input (str): Description of user_input.
        response (str): Description of response.
        tokens_used (Optional[int]): Description of tokens_used, default=None.
        metadata (Optional[dict]): Description of metadata, default=None.

    """
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
    emb = get_cached_embedding(response)
    with get_pgvector_repo(distance="cosine") as vrepo:
        vrepo.upsert(
            session_id=session_id,
            collection=config.memory.collection_name,
            embedding=emb,
            document=response,
            metadata={"session_id": session_id, **(metadata or {})},
            content_sha256=_sha256(response),
        )
