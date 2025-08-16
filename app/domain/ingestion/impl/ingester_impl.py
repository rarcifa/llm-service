"""Module documentation for `app/domain/ingestion/impl/chroma_ingester.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Iterable, List, Optional

from app.common.decorators.errors import error_boundary
from app.common.decorators.retry import with_retry
from app.common.utils.encoding import sha256
from app.common.utils.logger import setup_logger
from app.config import config
from app.db.repositories.pgvector_repository import get_pgvector_repo
from app.domain.ingestion.base.ingester_base import IngesterBase
from app.domain.ingestion.utils.ingestion_utils import chunk_text, safe_metadata
from app.domain.retrieval.utils.embeddings_utils import get_embedding_model
from app.enums.vector import DistanceMetric

logger = setup_logger()


class IngesterImpl(IngesterBase):
    """Summary of `PgVectorIngester`.

    Attributes:
        chunk_size: Description of `chunk_size`.
        collection: Description of `collection`.
        docs_root: Description of `docs_root`.
        model: Description of `model`.
        patterns: Description of `patterns`.
    """

    def __init__(self) -> None:
        """Summary of `__init__`.

        Args:
            self: Description of self.

        """
        self.model = get_embedding_model()
        self.collection = config.memory.collection_name
        self.chunk_size = config.retrieval.chunk_size
        self.docs_root = Path(config.retrieval.docs_path)
        self.patterns = list(config.retrieval.include_ext)
        self.docs_root.mkdir(parents=True, exist_ok=True)

    @error_boundary()
    def _embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """Summary of `_embed_chunks`.

        Args:
            self: Description of self.
            chunks (List[str]): Description of chunks.

        Returns:
            List[List[float]]: Description of return value.

        """
        return self.model.encode(chunks).tolist()

    @with_retry(max_retries=3)
    @error_boundary()
    def _ingest_file(self, file_path: Path) -> None:
        """Summary of `_ingest_file`.

        Args:
            self: Description of self.
            file_path (Path): Description of file_path.

        """
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(text, self.chunk_size)
        if not chunks:
            return
        vectors = self._embed_chunks(chunks)
        with get_pgvector_repo(distance=DistanceMetric.COSINE) as repo:
            for i, chunk in enumerate(chunks):
                emb = vectors[i]
                metadata = safe_metadata(
                    {"source": file_path.name, "path": str(file_path), "chunk": i}
                )
                repo.upsert(
                    collection=self.collection,
                    embedding=emb,
                    document=chunk,
                    metadata=metadata,
                    content_sha256=sha256(chunk),
                    id_override=str(uuid.uuid4()),
                )

    def ingest_paths(self, paths: Iterable[str | Path]) -> int:
        """Summary of `ingest_paths`.

        Args:
            self: Description of self.
            paths (Iterable[str | Path]): Description of paths.

        Returns:
            int: Description of return value.

        """
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
        """Summary of `ingest_glob`.

        Args:
            self: Description of self.
            root (Optional[str | Path]): Description of root, default=None.
            patterns (Optional[list[str]]): Description of patterns, default=None.

        Returns:
            int: Description of return value.

        """
        from glob import glob

        root_path = Path(root) if root else self.docs_root
        exts = patterns or self.patterns
        files: list[Path] = []
        for ext in exts:
            files.extend((Path(f) for f in glob(str(root_path / ext))))
        logger.info(
            "Found files to ingest",
            count=len(files),
            path=str(root_path),
            patterns=exts,
        )
        return self.ingest_paths(files)
