"""Module documentation for `app/domain/agent/base/agent_base.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class AgentBase(ABC):
    """Summary of `AgentBase`."""

    @abstractmethod
    def build(
        self, user_input: str
    ) -> Tuple[str, str, List[str], List[Dict[str, Any]]]:
        """Summary of `build`.

        Args:
            self: Description of self.
            user_input (str): Description of user_input.

        Returns:
            Tuple[str, str, List[str], List[Dict[str, Any]]]: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError
