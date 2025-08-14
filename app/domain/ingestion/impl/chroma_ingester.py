# app/domain/ingestion/impl/pgvector_ingester.py
from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Iterable, List, Optional

from app.common.decorators.errors import catch_and_log_errors
from app.common.decorators.retry import with_retry
from app.common.utils.logger import setup_logger
from app.config import CFG
from app.db.repositories.pgvector_repository import get_pgvector_repo
from app.domain.ingestion.base.ingester_base import IngesterBase
from app.domain.ingestion.utils.text import chunk_text
from app.domain.retrieval.utils.embeddings_utils import get_embedding_model

logger = setup_logger()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_metadata(meta: dict, *, max_len: int = 8192) -> dict:
    """Ensure pgvector JSONB metadata stores only JSON-serializable, small-ish values."""
    out = {}
    for k, v in (meta or {}).items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            out[k] = v
        else:
            s = str(v)
            out[k] = s if len(s) <= max_len else s[:max_len]
    return out


class PgVectorIngester(IngesterBase):
    """
    Ingests documents into Postgres (pgvector) using sentence-transformers embeddings.
    Reads config from manifest via CFG.retrieval.* and CFG.memory.collection_name.
    """

    def __init__(self) -> None:
        self.model = get_embedding_model()
        self.collection = CFG.memory.collection_name
        self.chunk_size = CFG.retrieval.chunk_size

        # root folder and globs come from manifest
        self.docs_root = Path(CFG.retrieval.docs_path)
        self.patterns = list(CFG.retrieval.include_ext)

        # ensure data dir exists (not strictly required, but nice to have)
        self.docs_root.mkdir(parents=True, exist_ok=True)

    @catch_and_log_errors()
    def _embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        # .tolist() to get vanilla Python lists for psycopg2-json serialization
        return self.model.encode(chunks).tolist()

    @with_retry(max_retries=3)
    @catch_and_log_errors()
    def _ingest_file(self, file_path: Path) -> None:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(text, self.chunk_size)
        if not chunks:
            return

        vectors = self._embed_chunks(chunks)

        with get_pgvector_repo(distance="cosine") as repo:
            for i, chunk in enumerate(chunks):
                emb = vectors[i]
                metadata = _safe_metadata(
                    {
                        "source": file_path.name,
                        "path": str(file_path),
                        "chunk": i,
                    }
                )
                repo.upsert(
                    collection=self.collection,
                    embedding=emb,
                    document=chunk,
                    metadata=metadata,
                    content_sha256=_sha256(chunk),
                    # optional: custom id; default inside repo is fine too
                    id_override=str(uuid.uuid4()),
                )

    def ingest_paths(self, paths: Iterable[str | Path]) -> int:
        count = 0
        for p in paths:
            p = Path(p)
            if p.is_file():
                self._ingest_file(p)
                count += 1
        logger.info(
            "Document ingestion complete", files=count, collection=self.collection
        )
        return count

    def ingest_glob(
        self, root: Optional[str | Path] = None, patterns: Optional[list[str]] = None
    ) -> int:
        from glob import glob

        root_path = Path(root) if root else self.docs_root
        exts = patterns or self.patterns

        files: list[Path] = []
        for ext in exts:
            files.extend(Path(f) for f in glob(str(root_path / ext)))
        logger.info(
            "Found files to ingest",
            count=len(files),
            path=str(root_path),
            patterns=exts,
        )
        return self.ingest_paths(files)
