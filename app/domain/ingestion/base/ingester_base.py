"""Module documentation for `app/domain/ingestion/base/ingester_base.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class IngesterBase(ABC):
    """Summary of `IngesterBase`."""

    @abstractmethod
    def ingest_paths(self, paths: Iterable[str]) -> int:
        """Summary of `ingest_paths`.

        Args:
            self: Description of self.
            paths (Iterable[str]): Description of paths.

        Returns:
            int: Description of return value.

        """
        ...

    @abstractmethod
    def ingest_glob(self, root: str, patterns: list[str]) -> int:
        """Summary of `ingest_glob`.

        Args:
            self: Description of self.
            root (str): Description of root.
            patterns (list[str]): Description of patterns.

        Returns:
            int: Description of return value.

        """
        ...
