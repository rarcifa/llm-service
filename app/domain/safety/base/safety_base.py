from __future__ import annotations
from abc import ABC, abstractmethod

class SafetyBase(ABC):
    """Abstract interface for text safety detectors."""
    @abstractmethod
    def detect(self, text: str) -> bool:
        """Return True if unsafe pattern is detected."""
        raise NotImplementedError

    """Abstract interface for text safety filters/transforms."""
    @abstractmethod
    def apply(self, text: str) -> str:
        """Return a sanitized/filtered version of the input text."""
        raise NotImplementedError
