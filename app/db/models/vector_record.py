"""Module documentation for `app/db/models/vector_record.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.db.postgres import Base

EMBED_DIM = 384


class VectorRecordModel(Base):
    """Summary of `VectorRecordModel`."""

    __tablename__ = "vector_records"
    __table_args__ = (
        UniqueConstraint(
            "content_sha256", "collection", name="uq_vec_content_collection"
        ),
    )
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    collection = Column(String, nullable=False)
    content_sha256 = Column(String(64), nullable=False, index=True)
    embedding = Column(Vector(EMBED_DIM), nullable=False)
    document = Column(Text, nullable=True)
    meta = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, nullable=False)
    session = relationship("SessionModel", back_populates="vector_records")
