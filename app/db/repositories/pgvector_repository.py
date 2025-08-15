"""Module documentation for `app/db/repositories/pgvector_repository.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pgvector import Vector
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.common.decorators.errors import catch_and_log_errors
from app.constants.errors import VECTOR_REPO_TOPK, VECTOR_REPO_UPSERT
from app.db.models.vector_record import VectorRecordModel
from app.db.postgres import SessionLocal


class PgVectorRepository:
    """Summary of `PgVectorRepository`.

    Attributes:
        _distance: Description of `_distance`.
        db: Description of `db`.
    """

    def __init__(self, db: Session, *, distance: str = "cosine") -> None:
        """Summary of `__init__`.

        Args:
            self: Description of self.
            db (Session): Description of db.
            distance (str): Description of distance, default='cosine'.

        """
        self.db = db
        self._distance = distance

    @catch_and_log_errors(default_return={"error": VECTOR_REPO_UPSERT})
    def upsert(
        self,
        *,
        collection: str,
        embedding: list[float],
        document: Optional[str],
        metadata: Optional[Dict[str, Any]],
        content_sha256: str,
        session_id: Optional[UUID] = None,
        id: Optional[UUID] = None,
    ) -> UUID:
        """Summary of `upsert`.

        Args:
            self: Description of self.
            collection (str): Description of collection.
            embedding (list[float]): Description of embedding.
            document (Optional[str]): Description of document.
            metadata (Optional[Dict[str, Any]]): Description of metadata.
            content_sha256 (str): Description of content_sha256.
            session_id (Optional[UUID]): Description of session_id, default=None.
            id (Optional[UUID]): Description of id, default=None.

        Returns:
            UUID: Description of return value.

        """
        rec_id = id or uuid4()
        stmt = (
            insert(VectorRecordModel)
            .values(
                id=rec_id,
                session_id=session_id,
                collection=collection,
                content_sha256=content_sha256,
                embedding=embedding,
                document=document,
                meta=metadata or {},
            )
            .on_conflict_do_update(
                constraint="uq_vec_content_collection",
                set_={
                    "embedding": embedding,
                    "document": document,
                    "metadata": metadata,
                },
            )
        )
        self.db.execute(stmt)
        self.db.commit()
        return rec_id

    @catch_and_log_errors(default_return={"error": VECTOR_REPO_TOPK})
    def topk(
        self, *, query_vec: list[float], collection: str, k: int = 5
    ) -> List[Dict[str, Any]]:
        """Summary of `topk`.

        Args:
            self: Description of self.
            query_vec (list[float]): Description of query_vec.
            collection (str): Description of collection.
            k (int): Description of k, default=5.

        Returns:
            List[Dict[str, Any]]: Description of return value.

        """
        if self._distance == "cosine":
            op = "<=>"
            score_sql = "1 - (embedding <=> :q)"
        elif self._distance == "l2":
            op = "<->"
            score_sql = "-(embedding <-> :q)"
        else:
            op = "<#>"
            score_sql = "-(embedding <#> :q)"
        rows = (
            self.db.execute(
                text(
                    f"\n                SELECT id::text, document, metadata, ({score_sql})::float AS score\n                FROM vector_records\n                WHERE collection = :col\n                ORDER BY embedding {op} :q\n                LIMIT :k\n            "
                ),
                {"q": Vector(query_vec), "col": collection, "k": k},
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows]


@contextmanager
def get_pgvector_repo(distance: str = "cosine"):
    """Summary of `get_pgvector_repo`.

    Args:
        distance (str): Description of distance, default='cosine'.

    Returns:
        Any: Description of return value.

    """
    db = SessionLocal()
    try:
        yield PgVectorRepository(db, distance=distance)
    finally:
        db.close()
