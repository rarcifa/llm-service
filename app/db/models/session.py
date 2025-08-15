"""Module documentation for `app/db/models/session.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.postgres import Base


class SessionModel(Base):
    """Summary of `SessionModel`."""

    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    messages = relationship(
        "MessageModel", back_populates="session", cascade="all, delete-orphan"
    )
    vector_records = relationship(
        "VectorRecordModel", back_populates="session", cascade="all, delete-orphan"
    )
