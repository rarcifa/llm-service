"""
postgres.py

Defines the SQLAlchemy engine, session factory, and init_db().
Model definitions live in app.models.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import os

from pgvector.psycopg2 import register_vector  # <-- add
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.common.decorators.errors import catch_and_log_errors
from app.enums.errors.postgres import PostgresErrorType

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost/llm_db"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()


@event.listens_for(engine, "connect")
def _register_pgvector(dbapi_conn, _):
    try:
        register_vector(
            dbapi_conn
        )  # ensures psycopg2 adapts Vector() params & reads vector columns
    except Exception:
        # don't crash app if it's already registered, or extension missing in a non-vector DB
        pass


@catch_and_log_errors(default_return={"error": PostgresErrorType.POSTGRES_INIT_DB})
def init_db() -> None:
    """
    Initializes the database by creating all declared tables.
    """
    Base.metadata.create_all(bind=engine)
