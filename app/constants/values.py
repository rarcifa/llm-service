"""Module documentation for `app/constants/values.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from pathlib import Path

USE_HTTP_API = True
OLLAMA_CLI = "ollama"
OLLAMA_CMD = "run"
CHROMA_COLLECTION_NAME = "agent_docs"
EMBEDDING_PATH: str = "./chroma_memory"
ENCODING = "utf-8"
DOCS_PATH = "./data"
CHUNK_SIZE = 300
SUPPORTED_EXT = ["*.txt", "*.md"]
MANIFEST_PATH = Path("manifest.yaml")
