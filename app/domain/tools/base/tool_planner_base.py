from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class ToolPlannerBase(ABC):
    """Abstract interface for generating a multi-step tool plan."""
    @abstractmethod
    def route(self, user_input: str) -> List[Dict[str, Any]]:
        """Return a list of steps, each like {'tool': str, 'input': str}."""
        raise NotImplementedError
