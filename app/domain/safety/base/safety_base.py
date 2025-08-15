"""Module documentation for `app/domain/safety/base/safety_base.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class SafetyBase(ABC):
    """Summary of `SafetyBase`."""

    @abstractmethod
    def detect(self, text: str) -> bool:
        """Summary of `detect`.

        Args:
            self: Description of self.
            text (str): Description of text.

        Returns:
            bool: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError

    "Abstract interface for text safety filters/transforms."

    @abstractmethod
    def apply(self, text: str) -> str:
        """Summary of `apply`.

        Args:
            self: Description of self.
            text (str): Description of text.

        Returns:
            str: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError
