"""Agent pipeline contract (base).

Defines the contract for building sanitized input, tool plan, context,
and the final rendered prompt. No concrete deps or config here.

Author: Ricardo Arcifa
Created: 2025-02-03
"""
from __future__ import annotations


from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class AgentBase(ABC):
    """Abstract interface for agent pipeline assembly."""

    @abstractmethod
    def build(
        self, user_input: str
    ) -> Tuple[str, str, List[str], List[Dict[str, Any]]]:
        """Assemble sanitized input, rendered prompt, context chunks, and tool plan.

        Args:
            user_input: Raw user input.

        Returns:
            (filtered_input, rendered_prompt, context_chunks, plan)
        """
        raise NotImplementedError