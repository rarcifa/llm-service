"""Module documentation for `app/domain/tools/base/tool_planner_base.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ToolPlannerBase(ABC):
    """Summary of `ToolPlannerBase`."""

    @abstractmethod
    def route(self, user_input: str) -> List[Dict[str, Any]]:
        """Summary of `route`.

        Args:
            self: Description of self.
            user_input (str): Description of user_input.

        Returns:
            List[Dict[str, Any]]: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError
