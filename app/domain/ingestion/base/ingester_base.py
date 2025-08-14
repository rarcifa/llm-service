from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class IngesterBase(ABC):
    @abstractmethod
    def ingest_paths(self, paths: Iterable[str]) -> int: ...
    @abstractmethod
    def ingest_glob(self, root: str, patterns: list[str]) -> int: ...
