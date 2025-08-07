"""
chat_router.py

Defines the FastAPI router for chat interactions with the LLM agent.
Includes synchronous and streaming endpoints for interacting with the model.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from fastapi import APIRouter, Depends, Request

from api.controllers.chat_controller import ChatController
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_chat_controller():
    """
    Dependency provider for ChatController instance.
    Returns a new ChatController using the ChatService.

    Returns:
        ChatController: Controller instance for handling chat requests.
    """
    return ChatController(ChatService())


@router.post("", summary="Chat with the LLM agent")
async def chat_route(
    request: Request, controller: ChatController = Depends(get_chat_controller)
):
    """
    POST /chat

    Handles a standard (non-streaming) chat request with the agent.
    Accepts a JSON payload containing `input` and optional `session_id`.

    Args:
        request (Request): The FastAPI request with user input.
        controller (ChatController): Dependency-injected controller.

    Returns:
        JSONResponse: The agent's response or an error.
    """
    return await controller.chat(request)


@router.post("/stream", summary="Stream Chat with the LLM agent")
async def stream_chat_route(
    request: Request, controller: ChatController = Depends(get_chat_controller)
):
    """
    POST /chat/stream

    Handles a streaming chat request, returning token-by-token output.
    Accepts a JSON payload with `input` and optional `session_id`.

    Args:
        request (Request): The FastAPI request with user input.
        controller (ChatController): Dependency-injected controller.

    Returns:
        StreamingResponse: A stream of agent response tokens as plain text.
    """
    return await controller.stream_chat(request)
