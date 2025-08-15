"""Module documentation for `app/domain/retrieval/base/retriever_base.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class RetrieverBase(ABC):
    """Summary of `RetrieverBase`."""

    @abstractmethod
    def retrieve(self, query: str, *, top_k: int = 4) -> List[str]:
        """Summary of `retrieve`.

        Args:
            self: Description of self.
            query (str): Description of query.
            top_k (int): Description of top_k, default=4.

        Returns:
            List[str]: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError

    @abstractmethod
    def query(self, question: str, *, top_k: int = 4) -> str:
        """Summary of `query`.

        Args:
            self: Description of self.
            question (str): Description of question.
            top_k (int): Description of top_k, default=4.

        Returns:
            str: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError
