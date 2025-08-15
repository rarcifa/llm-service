"""Module documentation for `app/db/schemas/chat.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Summary of `ChatRequest`."""

    input: str = Field(
        ...,
        description="The user's input prompt.",
        example="What's the weather like today?",
    )
    session_id: str | None = Field(
        None, description="Optional session ID for conversation continuity."
    )
