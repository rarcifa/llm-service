"""Module documentation for `app/db/schemas/session.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.db.schemas.message import MessageResponse


class SessionBase(BaseModel):
    """Summary of `SessionBase`."""

    pass


class SessionCreate(BaseModel):
    """Summary of `SessionCreate`."""

    metadata: Optional[dict] = None


class SessionResponse(BaseModel):
    """Summary of `SessionResponse`."""

    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class SessionTranscript(SessionResponse):
    """Summary of `SessionTranscript`."""

    messages: List[MessageResponse]
