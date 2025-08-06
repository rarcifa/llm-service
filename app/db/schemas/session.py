from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.db.schemas.message import MessageResponse


class SessionBase(BaseModel):
    pass


class SessionCreate(BaseModel):
    metadata: Optional[dict] = None


class SessionResponse(BaseModel):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class SessionTranscript(SessionResponse):
    messages: List[MessageResponse]
