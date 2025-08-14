from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pgvector import Vector
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.models.vector_record import VectorRecordModel
from app.db.postgres import SessionLocal


class PgVectorRepository:
    def __init__(self, db: Session, *, distance: str = "cosine") -> None:
        self.db = db
        self._distance = distance  # "cosine" | "l2" | "ip"

    # --- writes ---
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

    # --- reads ---
    def topk(
        self, *, query_vec: list[float], collection: str, k: int = 5
    ) -> List[Dict[str, Any]]:
        if self._distance == "cosine":
            op = "<=>"  # cosine distance
            score_sql = "1 - (embedding <=> :q)"  # cosine similarity
        elif self._distance == "l2":
            op = "<->"
            score_sql = "-(embedding <-> :q)"  # convert distance to similarity
        else:  # "ip"
            op = "<#>"
            score_sql = "-(embedding <#> :q)"

        rows = (
            self.db.execute(
                text(
                    f"""
                SELECT id::text, document, metadata, ({score_sql})::float AS score
                FROM vector_records
                WHERE collection = :col
                ORDER BY embedding {op} :q
                LIMIT :k
            """
                ),
                {
                    "q": Vector(query_vec),  # <-- key change: adapt to pgvector
                    "col": collection,
                    "k": k,
                },
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows]


from contextlib import contextmanager


@contextmanager
def get_pgvector_repo(distance: str = "cosine"):
    db = SessionLocal()
    try:
        yield PgVectorRepository(db, distance=distance)
    finally:
        db.close()
