"""
session_repository.py

Handles database interactions for storing and retrieving chat sessions and messages.

This repository provides a persistent backing for session continuity,
message history, and logging of user-agent conversations.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.common.decorators.errors import catch_and_log_errors
from app.db.models.message import MessageModel
from app.db.models.session import SessionModel
from app.db.postgres import SessionLocal
from app.enums.errors.session_repository import SessionRepoErrorType


class SessionRepository:
    """
    Repository for managing chat sessions and messages.
    This class assumes that a DB session is injected externally (e.g. via FastAPI's Depends).
    """

    def __init__(self, db: Session):
        """
        Initializes a new database session.
        """
        self.db = db

    @catch_and_log_errors(
        default_return={"error": SessionRepoErrorType.SESSION_REPO_GET_SESSION_BY_ID}
    )
    def get_session_by_id(self, session_id: UUID) -> Optional[SessionModel]:
        """
        Retrieve a session by its unique ID.

        Args:
            session_id (UUID): The unique identifier of the session.

        Returns:
            Optional[SessionModel]: The session object if found, otherwise None.
        """
        return self.db.query(SessionModel).filter_by(id=session_id).first()

    @catch_and_log_errors(
        default_return={"error": SessionRepoErrorType.SESSION_REPO_CREATE_SESSION}
    )
    def create_session(
        self, session_id: Optional[UUID] = None, metadata: Optional[dict] = None
    ) -> SessionModel:
        """
        Create a new session with optional metadata.

        Args:
            session_id (Optional[UUID]): A predefined UUID for the session (auto-generated if None).
            metadata (Optional[dict]): Optional session metadata for traceability or context.

        Returns:
            SessionModel: The newly created session object.
        """
        session = SessionModel(id=session_id, metadata=metadata)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    @catch_and_log_errors(
        default_return={"error": SessionRepoErrorType.SESSION_REPO_CREATE_SESSION}
    )
    def get_or_create_session(self, session_id: UUID) -> SessionModel:
        """
        Retrieves an existing session or creates a new one if it doesn't exist.

        Args:
            session_id (str): The UUID for the session.

        Returns:
            Session: SQLAlchemy session object.
        """
        session = self.get_session_by_id(session_id)
        if session:
            return session
        return self.create_session(session_id=session_id)

    @catch_and_log_errors(
        default_return={"error": SessionRepoErrorType.SESSION_REPO_STORE_MESSAGE}
    )
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
        """
        Stores a message associated with a session.

        Args:
            session_id (str): The session ID the message belongs to.
            message_id (str): Unique identifier for the message.
            role (str): The sender's role ('user' or 'agent').
            content (str): The content of the message.
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

    @catch_and_log_errors(
        default_return={"error": SessionRepoErrorType.SESSION_REPO_GET_MESSAGES}
    )
    def get_messages_for_session(self, session_id: UUID) -> List[MessageModel]:
        """
        Retrieves the full message history for a session, ordered by timestamp.

        Args:
            session_id (str): The session ID to retrieve messages for.

        Returns:
            list[str]: List of formatted messages in the form "User: ...", "Agent: ..."
        """
        return (
            self.db.query(MessageModel)
            .filter_by(session_id=session_id)
            .order_by(MessageModel.created_at)
            .all()
        )


@contextmanager
def get_session_repo():
    """
    Yields a SessionRepository instance with automatic DB session management.
    Use this in non-FastAPI contexts (agents, jobs, etc.).
    """
    db = SessionLocal()
    try:
        yield SessionRepository(db)
    finally:
        db.close()
