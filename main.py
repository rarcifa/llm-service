"""
main.py

Main FastAPI application entry point for the Enterprise Agent API.
Initializes the database, loads routers, and configures lifecycle hooks.

Author: Ricardo Arcifa
Created: 2025-02-03
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
    """
    Executes startup tasks when the FastAPI app is initialized.

    - Initializes database connections (e.g., Postgres).
    - Can be extended to load memory, preload models, etc.
    """
    init_db()


# Register chat-related routes
app.include_router(chat_router)
