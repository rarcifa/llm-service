# app/db/chroma.py
from __future__ import annotations
from functools import lru_cache
from typing import Optional, Dict, Any

from chromadb import PersistentClient

@lru_cache(maxsize=1)
def get_chroma_client(path: str) -> PersistentClient:
    """
    Return a memoized PersistentClient for the given path.
    Always call through here to avoid multiple client instances with different settings.
    """
    return PersistentClient(path=path)

def get_or_create_collection(
    *, path: str, name: str, metadata: Optional[Dict[str, Any]] = None, metric: str = "cosine"
):
    """
    Return a Chroma collection object (not a string).
    """
    md = dict(metadata or {})
    # Some setups use 'hnsw:space' to indicate cosine/ L2, etc.
    md.setdefault("hnsw:space", metric)

    client = get_chroma_client(path)
    return client.get_or_create_collection(name=name, metadata=md)
