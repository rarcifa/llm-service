"""
load_documents.py

Loads and ingests supported text documents from the local `./data` directory
into a ChromaDB vector collection using sentence-transformer embeddings.

Each document is:
- Split into chunks of fixed size
- Embedded into a vector
- Persisted in the vector DB with metadata for traceability

Supported file types:
- `.txt`
- `.md`

Usage:
    python load_documents.py

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import glob
import os
import uuid
from pathlib import Path

import chromadb

from app.constants.values import (
    CHROMA_COLLECTION_NAME,
    CHUNK_SIZE,
    DOCS_PATH,
    EMBEDDING_PATH,
    ENCODING,
    SUPPORTED_EXT,
)
from app.lib.embeddings.embeddings_utils import get_embedding_model
from app.lib.utils.decorators.errors import catch_and_log_errors
from app.lib.utils.decorators.retry import with_retry
from app.lib.utils.logger import setup_logger

logger = setup_logger()

# === Setup persistent vector DB and embedding model ===
embedding_model = get_embedding_model()
chroma = chromadb.PersistentClient(path=EMBEDDING_PATH)
collection = chroma.get_or_create_collection(name=CHROMA_COLLECTION_NAME)


def chunk_text(text: str, size: int = CHUNK_SIZE) -> list[str]:
    """
    Splits a document into fixed-size character chunks.

    Args:
        text (str): Full text of the document.
        size (int, optional): Size of each chunk. Defaults to CHUNK_SIZE.

    Returns:
        list[str]: List of text chunks.
    """
    return [text[i : i + size] for i in range(0, len(text), size)]


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """
    Embeds a list of text chunks into vector space using sentence-transformers.

    Args:
        chunks (list[str]): List of textual chunks.

    Returns:
        list[list[float]]: Corresponding embedding vectors.
    """
    return embedding_model.encode(chunks).tolist()


def find_supported_files() -> list[str]:
    """
    Finds all supported text files in the configured document directory.

    Returns:
        list[str]: List of file paths to supported text files.
    """
    files = []
    for ext in SUPPORTED_EXT:
        files.extend(glob.glob(os.path.join(DOCS_PATH, ext)))
    return files


@with_retry(max_retries=3)
@catch_and_log_errors()
def ingest_file(file_path: str) -> None:
    """
    Ingests a single file: reads it, chunks it, embeds the chunks, and stores them in ChromaDB.

    Args:
        file_path (str): Path to the file to ingest.
    """
    with open(file_path, "r", encoding=ENCODING) as f:
        content = f.read()

    chunks = chunk_text(content)
    embeddings = embed_chunks(chunks)

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeddings[i]],
            ids=[str(uuid.uuid4())],
            metadatas=[{"source": Path(file_path).name, "chunk": i}],
        )


@catch_and_log_errors()
def load_files() -> int:
    """
    Main entrypoint to ingest all supported files from DOCS_PATH.

    Returns:
        int: Number of files successfully processed.
    """
    files = find_supported_files()
    logger.info("Found files to ingest", count=len(files), path=DOCS_PATH)

    for path in files:
        ingest_file(path)

    logger.info("Document ingestion complete")
    return len(files)


if __name__ == "__main__":
    load_files()
