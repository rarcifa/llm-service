"""Module documentation for `app/db/repositories/session_repository.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.common.decorators.errors import error_boundary
from app.constants.errors import (
    SESSION_REPO_CREATE_SESSION,
    SESSION_REPO_GET_MESSAGES,
    SESSION_REPO_GET_SESSION_BY_ID,
    SESSION_REPO_STORE_MESSAGE,
)
from app.db.models.message import MessageModel
from app.db.models.session import SessionModel
from app.db.postgres import SessionLocal


class SessionRepository:
    """Summary of `SessionRepository`.

    Attributes:
        db: Description of `db`.
    """

    def __init__(self, db: Session):
        """Summary of `__init__`.

        Args:
            self: Description of self.
            db (Session): Description of db.

        Returns:
            Any: Description of return value.

        """
        self.db = db

    @error_boundary(default_return={"error": SESSION_REPO_GET_SESSION_BY_ID})
    def get_session_by_id(self, session_id: UUID) -> Optional[SessionModel]:
        """Summary of `get_session_by_id`.

        Args:
            self: Description of self.
            session_id (UUID): Description of session_id.

        Returns:
            Optional[SessionModel]: Description of return value.

        """
        return self.db.query(SessionModel).filter_by(id=session_id).first()

    @error_boundary(default_return={"error": SESSION_REPO_CREATE_SESSION})
    def create_session(
        self, session_id: Optional[UUID] = None, metadata: Optional[dict] = None
    ) -> SessionModel:
        """Summary of `create_session`.

        Args:
            self: Description of self.
            session_id (Optional[UUID]): Description of session_id, default=None.
            metadata (Optional[dict]): Description of metadata, default=None.

        Returns:
            SessionModel: Description of return value.

        """
        session = SessionModel(id=session_id, metadata=metadata)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    @error_boundary(default_return={"error": SESSION_REPO_CREATE_SESSION})
    def get_or_create_session(self, session_id: UUID) -> SessionModel:
        """Summary of `get_or_create_session`.

        Args:
            self: Description of self.
            session_id (UUID): Description of session_id.

        Returns:
            SessionModel: Description of return value.

        """
        session = self.get_session_by_id(session_id)
        if session:
            return session
        return self.create_session(session_id=session_id)

    @error_boundary(default_return={"error": SESSION_REPO_STORE_MESSAGE})
    def store_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        message_id: Optional[UUID] = None,
        tokens_used: Optional[int] = None,
        feedback: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> MessageModel:
        """Summary of `store_message`.

        Args:
            self: Description of self.
            session_id (UUID): Description of session_id.
            role (str): Description of role.
            content (str): Description of content.
            message_id (Optional[UUID]): Description of message_id, default=None.
            tokens_used (Optional[int]): Description of tokens_used, default=None.
            feedback (Optional[dict]): Description of feedback, default=None.
            metadata (Optional[dict]): Description of metadata, default=None.

        Returns:
            MessageModel: Description of return value.

        """
        message = MessageModel(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            created_at=datetime.utcnow(),
            tokens_used=tokens_used,
            feedback=feedback,
            message_metadata=metadata,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    @error_boundary(default_return={"error": SESSION_REPO_GET_MESSAGES})
    def get_messages_for_session(self, session_id: UUID) -> List[MessageModel]:
        """Summary of `get_messages_for_session`.

        Args:
            self: Description of self.
            session_id (UUID): Description of session_id.

        Returns:
            List[MessageModel]: Description of return value.

        """
        return (
            self.db.query(MessageModel)
            .filter_by(session_id=session_id)
            .order_by(MessageModel.created_at)
            .all()
        )


@contextmanager
def get_session_repo():
    """Summary of `get_session_repo`.

    Args:
        (no arguments)

    Returns:
        Any: Description of return value.

    """
    db = SessionLocal()
    try:
        yield SessionRepository(db)
    finally:
        db.close()
