"""Module documentation for `app/domain/eval/base/eval_base.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EvalBase(ABC):
    """Summary of `EvalBase`."""

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
        """Summary of `run`.

        Args:
            self: Description of self.
            filtered_input (str): Description of filtered_input.
            response (str): Description of response.
            retrieved_docs (list[str]): Description of retrieved_docs.
            response_id (str): Description of response_id.
            message_id (str): Description of message_id.
            session_id (str): Description of session_id.
            prompt_version (str | None): Description of prompt_version, default=None.
            template_name (str | None): Description of template_name, default=None.
            system_prompt (str | None): Description of system_prompt, default=None.
            rendered_prompt (str | None): Description of rendered_prompt, default=None.
            raw_input (str | None): Description of raw_input, default=None.
            conversation_history (list[str] | None): Description of conversation_history, default=None.

        Returns:
            dict[str, Any]: Description of return value.

        Raises:
            NotImplementedError: Condition when this is raised.

        """
        raise NotImplementedError
