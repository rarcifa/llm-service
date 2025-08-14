"""
postgres.py

Defines the SQLAlchemy engine, session factory, and init_db().
Model definitions live in app.models.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.enums.errors.postgres import PostgresErrorType
from app.common.decorators.errors import catch_and_log_errors

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost/llm_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@catch_and_log_errors(default_return={"error": PostgresErrorType.POSTGRES_INIT_DB})
def init_db() -> None:
    """
    Initializes the database by creating all declared tables.
    """
    Base.metadata.create_all(bind=engine)
