"""Module documentation for `app/domain/tools/base/step_executor_base.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class StepExecutorBase(ABC):
    """Summary of `StepExecutorBase`."""

    @abstractmethod
    def execute(self, plan: List[Dict[str, Any]]) -> Any:
        """Summary of `execute`.

        Args:
            self: Description of self.
            plan (List[Dict[str, Any]]): Description of plan.

        Returns:
            Any: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError
