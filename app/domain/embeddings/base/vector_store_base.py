from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol


class VectorCollection(Protocol):
    """Minimal Chroma-like API for collections."""
    def add(
        self,
        *,
        documents: List[str],
        embeddings: List[List[float]],
        ids: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None: ...
    def query(
        self,
        *,
        query_embeddings: List[List[float]],
        n_results: int,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]: ...


class VectorStoreBase(ABC):
    """Abstract interface for a vector store backend."""
    @abstractmethod
    def get_collection(self, name: Optional[str] = None) -> VectorCollection:
        """Return (and possibly cache) a named vector collection."""
        raise NotImplementedError
