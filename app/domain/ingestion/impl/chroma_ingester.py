from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Iterable, List

from app.common.decorators.errors import catch_and_log_errors
from app.common.decorators.retry import with_retry
from app.common.utils.logger import setup_logger
from app.constants.values import (
    CHROMA_COLLECTION_NAME,
    CHUNK_SIZE,
    DOCS_PATH,
    EMBEDDING_PATH,
    ENCODING,
    SUPPORTED_EXT,
)
from app.domain.embeddings.impl.embeddings_impl import EmbeddingsImpl
from app.domain.embeddings.utils.embeddings_utils import get_embedding_model
from app.domain.ingestion.base.ingester_base import IngesterBase
from app.domain.ingestion.utils.text import chunk_text

logger = setup_logger()

class ChromaIngester(IngesterBase):
    """Ingest .txt/.md documents into Chroma using sentence-transformer embeddings."""

    def __init__(self) -> None:
        self.model = get_embedding_model()
        # reuse your existing Chroma wrapper to avoid duplicate clients
        self.emb = EmbeddingsImpl(path=str(EMBEDDING_PATH))
        self.collection = self.emb.get_collection(CHROMA_COLLECTION_NAME)
        os.makedirs(str(EMBEDDING_PATH), exist_ok=True)

    @catch_and_log_errors()
    def _embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        return self.model.encode(chunks).tolist()

    @with_retry(max_retries=3)
    @catch_and_log_errors()
    def _ingest_file(self, file_path: str) -> None:
        with open(file_path, "r", encoding=ENCODING) as f:
            content = f.read()

        chunks = chunk_text(content, CHUNK_SIZE)
        vectors = self._embed_chunks(chunks)

        for i, chunk in enumerate(chunks):
            self.collection.add(
                documents=[chunk],
                embeddings=[vectors[i]],
                ids=[str(uuid.uuid4())],
                metadatas=[{"source": Path(file_path).name, "chunk": i}],
            )

    def ingest_paths(self, paths: Iterable[str]) -> int:
        count = 0
        for p in paths:
            self._ingest_file(p)
            count += 1
        logger.info("Document ingestion complete", files=count)
        return count

    def ingest_glob(self, root: str = str(DOCS_PATH), patterns: list[str] = None) -> int:
        import glob, os as _os
        patterns = patterns or SUPPORTED_EXT
        files: list[str] = []
        for ext in patterns:
            files.extend(glob.glob(_os.path.join(root, ext)))
        logger.info("Found files to ingest", count=len(files), path=root)
        return self.ingest_paths(files)
