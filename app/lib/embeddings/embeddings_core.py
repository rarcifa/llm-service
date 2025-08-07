"""
memory_manager.py

Manages semantic memory storage and retrieval using ChromaDB with vector embeddings.
Embeds user-agent conversations and supports contextual retrieval based on similarity.

Used to augment prompts with relevant history (e.g., for ReAct, RAG, or chat memory).

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.lib.embeddings.chroma import get_chroma_collection
from app.lib.embeddings.embeddings_utils import get_cached_embedding
from app.lib.utils.decorators.errors import catch_and_log_errors


class EmbeddingsCore:
    """
    Handles semantic memory storage and retrieval using ChromaDB.

    Attributes:
        collection (chromadb.api.models.Collection.Collection): Vector DB collection used for memory.
        window_size (int): Number of top documents to retrieve for context.
    """

    def __init__(self, memory_config: dict) -> None:
        """
        Initializes the memory manager with the configured window size and collection.

        Args:
            memory_config (dict): Configuration dictionary with optional 'window_size'.
        """
        self.collection = get_chroma_collection()
        self.window_size = memory_config.get("window_size", 3)

    @catch_and_log_errors()
    def store_interaction(self, user_input: str, agent_response: str) -> None:
        """
        Stores a user-agent interaction in semantic memory.

        Args:
            user_input (str): The user's original input.
            agent_response (str): The agent's response to the input.
        """
        combined_text = f"User: {user_input}\nAgent: {agent_response}"
        embedding = get_cached_embedding(combined_text)

        # Store document and its embedding with metadata
        self.collection.add(
            documents=[combined_text],
            embeddings=[embedding],
            ids=[str(uuid.uuid4())],
            metadatas=[{"timestamp": datetime.now(timezone.utc).isoformat()}],
        )

    @catch_and_log_errors(default_return=[])
    def retrieve_context(self, query: str) -> list[str]:
        """
        Retrieves the top-k most relevant memory entries for a given query.

        Args:
            query (str): The input query to search memory against.

        Returns:
            list[str]: A list of document strings from memory, ranked by similarity.
        """
        query_embedding = get_cached_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding], n_results=self.window_size
        )
        return results.get("documents", [[]])[0]
