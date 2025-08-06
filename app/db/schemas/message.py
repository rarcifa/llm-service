from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    role: str = Field(..., example="user")  # 'user' or 'agent'
    content: str = Field(..., example="What is CLM?")


class MessageCreate(MessageBase):
    session_id: UUID


class MessageResponse(MessageBase):
    id: UUID
    session_id: UUID
    created_at: datetime
    tokens_used: Optional[int] = None
    feedback: Optional[dict] = None
    metadata: Optional[dict] = None

    class Config:
        orm_mode = True
