"""Persistent Chroma collection accessor (via shared client)."""

from __future__ import annotations
from typing import Dict, Optional

from app.domain.embeddings.base.vector_store_base import VectorStoreBase, VectorCollection
from app.db.chroma import get_or_create_collection, get_chroma_client

class EmbeddingsImpl(VectorStoreBase):
    """Manages access to Chroma collections; no client duplication."""

    def __init__(self, path: str, default_collection: str | None = None) -> None:
        self._path = path
        self._default_name = default_collection
        self._cache: Dict[str, VectorCollection] = {}

    def get_client(self):
        # optional: expose client if someone really needs it
        return get_chroma_client(self._path)

    def get_collection(self, name: Optional[str] = None) -> VectorCollection:
        coll_name = name or self._default_name
        if not coll_name:
            raise ValueError("Collection name must be provided or set as default_collection.")
        if coll_name in self._cache:
            return self._cache[coll_name]
        collection = get_or_create_collection(path=self._path, name=coll_name)
        self._cache[coll_name] = collection
        return collection
