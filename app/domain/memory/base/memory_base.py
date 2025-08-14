from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class MemoryBase(ABC):
    """Abstract interface for semantic memory storage and retrieval."""

    @abstractmethod
    def store_interaction(self, user_input: str, agent_response: str) -> None:
        """Persist a single user–agent turn into memory."""
        raise NotImplementedError

    @abstractmethod
    def retrieve_context(self, query: str) -> List[str]:
        """Fetch top-k relevant context strings for a query."""
        raise NotImplementedError
