"""Module documentation for `app/domain/provider/base/provider_base.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, Union

Message = Dict[str, str]


class ProviderBase(ABC):
    """Summary of `ProviderBase`."""

    @abstractmethod
    def stream(
        self, messages: List[Message], **kwargs: Any
    ) -> Generator[str, None, None]:
        """Summary of `stream`.

        Args:
            self: Description of self.
            messages (List[Message]): Description of messages.
            kwargs (Any): Description of kwargs.

        Returns:
            Generator[str, None, None]: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError
