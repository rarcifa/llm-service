"""Abstract interface for evaluation services.

Author: Ricardo Arcifa
Created: 2025-02-03
"""
from __future__ import annotations


from abc import ABC, abstractmethod
from typing import Any


class EvalBase(ABC):
    """Contract for evaluating agent responses."""

    @abstractmethod
    def run(
        self,
        *,
        filtered_input: str,
        response: str,
        retrieved_docs: list[str],
        response_id: str,
        message_id: str,
        session_id: str,
        prompt_version: str | None = None,
        template_name: str | None = None,
        system_prompt: str | None = None,
        rendered_prompt: str | None = None,
        raw_input: str | None = None,
        conversation_history: list[str] | None = None,
    ) -> dict[str, Any]:
        """Evaluate a response and return structured scores/metadata."""
        raise NotImplementedError