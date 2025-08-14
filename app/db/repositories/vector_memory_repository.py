# app/db/repositories/vector_memory_repository.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
import json

from app.db.chroma import get_or_create_collection  # or your integrations/chroma_client

ALLOWED_TYPES = (str, int, float, bool, type(None))

def _sanitize_metadatas(metadatas: Optional[List[Dict[str, Any]]], *, max_len: int = 8192) -> List[Dict[str, Any]]:
    if not metadatas:
        return [{}]
    out: List[Dict[str, Any]] = []
    for meta in metadatas:
        safe: Dict[str, Any] = {}
        if not isinstance(meta, dict):
            meta = {"value": meta}
        for k, v in meta.items():
            if isinstance(v, ALLOWED_TYPES):
                safe[k] = v
            else:
                s = json.dumps(v, ensure_ascii=False)
                # optional: truncate to keep Chroma happy if you store large blobs
                if isinstance(s, str) and len(s) > max_len:
                    s = s[:max_len]
                safe[k] = s
        out.append(safe)
    return out

class VectorMemoryRepository:
    def __init__(self, *, path: str, collection_name: str, metric: str = "cosine") -> None:
        self.collection = get_or_create_collection(path=path, name=collection_name, metric=metric)

    def add_vectors(
        self, *, ids: List[str], embeddings: List[List[float]],
        documents: Optional[List[str]] = None, metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        n = len(ids)
        documents = documents or [None] * n  # type: ignore[list-item]
        metadatas = _sanitize_metadatas(metadatas or [{} for _ in range(n)])
        self.collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    def upsert_vectors(
        self, *, ids: List[str], embeddings: List[List[float]],
        documents: Optional[List[str]] = None, metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        n = len(ids)
        documents = documents or [None] * n  # type: ignore[list-item]
        metadatas = _sanitize_metadatas(metadatas or [{} for _ in range(n)])
        if hasattr(self.collection, "upsert"):
            self.collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        else:
            self.collection.delete(ids=ids)
            self.collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    def delete_ids(self, ids: List[str]) -> None:
        self.collection.delete(ids=ids)

    def similarity_search_by_vector(
        self, *, query_vector: List[float], top_k: int = 5, include_embeddings: bool = False
    ) -> List[Dict[str, Any]]:
        # Only allowed includes
        include = ["documents", "metadatas", "distances"]
        if include_embeddings:
            include.append("embeddings")

        res = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=include,
        )

        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        # 'ids' may be present even if not requested; handle gracefully if missing
        ids = (res.get("ids") or [[]])[0] if "ids" in res else [None] * len(docs)

        out: List[Dict[str, Any]] = []
        for i in range(len(docs)):
            dist = dists[i] if i < len(dists) else None
            sim = (1.0 - float(dist)) if dist is not None else None  # cosine distance -> similarity
            out.append({
                "id": ids[i] if i < len(ids) else None,
                "chunk": docs[i],
                "score": sim,
                "metadata": metas[i] if i < len(metas) else {},
            })
        return out
