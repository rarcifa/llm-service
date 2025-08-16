"""Module documentation for `app/db/schemas/eval.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvalRequest(BaseModel):
    """Summary of `EvalRequest`."""

    filtered_input: str = Field(..., description="The preprocessed user input.")
    response: str = Field(..., description="The final response from the agent.")
    retrieved_docs: List[Any] = Field(
        default_factory=list, description="Documents retrieved during context building."
    )
    response_id: str = Field(..., description="Unique identifier for this response.")
    message_id: str = Field(..., description="Unique identifier for the message.")
    session_id: str = Field(..., description="Identifier for the user session.")
    rendered_prompt: str = Field(..., description="The fully rendered prompt.")
    raw_input: str = Field(..., description="The raw user input text.")
    conversation_history: Optional[List[str]] = Field(
        default=None, description="Optional conversation history for the session."
    )
