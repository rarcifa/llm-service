"""
chroma.py

Handles initialization and access to ChromaDB persistent collections
for vector storage and retrieval, used for memory or document embeddings.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from typing import Union

import chromadb

# === Setup persistent Chroma client and embedding model ===
chroma = chromadb.PersistentClient(path="./chroma_memory")


def get_chroma_collection(
    name: Union[str, None] = "agent_memory",
) -> chromadb.api.models.Collection.Collection:
    """
    Retrieves or creates a Chroma collection with the given name.

    Args:
        name (str, optional): The name of the collection to retrieve or create.
            Defaults to "agent_memory".

    Returns:
        chromadb.api.models.Collection.Collection: The Chroma collection object.
    """
    return chroma.get_or_create_collection(name=name)
