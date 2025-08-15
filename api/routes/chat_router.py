"""Module documentation for `api/routes/chat_router.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from fastapi import APIRouter, Depends, Request

from api.controllers.chat_controller import ChatController
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_chat_controller():
    """Summary of `get_chat_controller`.

    Args:
        (no arguments)

    Returns:
        Any: Description of return value.

    """
    return ChatController(ChatService())


@router.post("", summary="Stream Chat with the LLM agent")
async def chat_route(
    request: Request, controller: ChatController = Depends(get_chat_controller)
):
    """Summary of `chat_route`.

    Args:
        request (Request): Description of request.
        controller (ChatController): Description of controller, default=Depends(get_chat_controller).

    Returns:
        Any: Description of return value.

    """
    return await controller.chat(request)
