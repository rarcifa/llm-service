"""Module documentation for `app/db/postgres.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import os

from pgvector.psycopg2 import register_vector
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
    """Summary of `_register_pgvector`.

    Args:
        dbapi_conn: Description of dbapi_conn.
        _: Description of _.

    Returns:
        Any: Description of return value.

    """
    try:
        register_vector(dbapi_conn)
    except Exception:
        pass


@catch_and_log_errors(default_return={"error": PostgresErrorType.POSTGRES_INIT_DB})
def init_db() -> None:
    """Summary of `init_db`.

    Args:
        (no arguments)

    """
    Base.metadata.create_all(bind=engine)
