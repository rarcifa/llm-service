from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class StepExecutorBase(ABC):
    """Abstract interface for executing a multi-step tool plan."""
    @abstractmethod
    def execute(self, plan: List[Dict[str, Any]]) -> Any:
        """Execute steps and return the final tool's output."""
        raise NotImplementedError
