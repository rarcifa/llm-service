"""Module documentation for `app/services/eval_service.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations
from typing import Any

from app.domain.eval.impl.eval_impl import EvalImpl
from app.enums.prompts import JsonKey


class EvalService:
    """Summary of `EvalService`.

    Attributes:
        eval_impl: Description of `eval_impl`.
    """

    def __init__(self) -> None:
        """Summary of `__init__`.

        Args:
            self: Description of self.

        Returns:
            Any: Description of return value.

        """
        self.eval_impl = EvalImpl()

    def run(
        self,
        filtered_input: str,
        response: str,
        retrieved_docs: list[Any],
        response_id: str,
        message_id: str,
        session_id: str,
        rendered_prompt: str,
        raw_input: str,
        conversation_history: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Run evaluation with explicit arguments.

        Args:
            filtered_input (str): The preprocessed user input.
            response (str): The final response from the agent.
            retrieved_docs (list[Any]): Documents retrieved during context building.
            response_id (str): Unique identifier for this response.
            message_id (str): Unique identifier for the originating message.
            session_id (str): Identifier for the user session.
            rendered_prompt (str): The fully rendered prompt sent to the model.
            raw_input (str): The raw user input text.
            conversation_history (list[dict[str, Any]] | None): Session conversation history.

        Returns:
            Any: The result returned by `EvalImpl.run`.
        """
        return self.eval_impl.run(
            filtered_input=filtered_input,
            response=response,
            retrieved_docs=retrieved_docs,
            response_id=response_id,
            message_id=message_id,
            session_id=session_id,
            rendered_prompt=rendered_prompt,
            raw_input=raw_input,
            conversation_history=conversation_history,
        )


Eval_service = EvalService()
