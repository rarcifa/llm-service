"""Module documentation for `app/domain/memory/base/memory_base.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class MemoryBase(ABC):
    """Summary of `MemoryBase`."""

    @abstractmethod
    def store_interaction(self, user_input: str, agent_response: str) -> None:
        """Summary of `store_interaction`.

        Args:
            self: Description of self.
            user_input (str): Description of user_input.
            agent_response (str): Description of agent_response.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError

    @abstractmethod
    def retrieve_context(self, query: str) -> List[str]:
        """Summary of `retrieve_context`.

        Args:
            self: Description of self.
            query (str): Description of query.

        Returns:
            List[str]: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError
