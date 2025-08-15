"""Module documentation for `app/db/schemas/message.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    """Summary of `MessageBase`."""

    role: str = Field(..., example="user")
    content: str = Field(..., example="What is CLM?")


class MessageCreate(MessageBase):
    """Summary of `MessageCreate`."""

    session_id: UUID


class MessageResponse(MessageBase):
    """Summary of `MessageResponse`."""

    id: UUID
    session_id: UUID
    created_at: datetime
    tokens_used: Optional[int] = None
    feedback: Optional[dict] = None
    metadata: Optional[dict] = None

    class Config:
        orm_mode = True
