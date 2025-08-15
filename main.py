"""Module documentation for `main.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from fastapi import FastAPI

from api.routes.chat_router import router as chat_router
from app.db.postgres import init_db

app = FastAPI(
    title="Enterprise Agent API",
    description="A modular LLM-powered API for interactive and streaming chat with evaluation support.",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    """Summary of `startup_event`.

    Args:
        (no arguments)

    Returns:
        Any: Description of return value.

    """
    init_db()


app.include_router(chat_router)
