"""
chat_controller.py

Defines the ChatController responsible for handling API requests related to
chat interactions with the LLM agent. Delegates to the ChatService for core logic.

Supports:
- Synchronous chat (`POST /chat`)
- Streaming chat (`POST /chat/stream`)

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.db.schemas.chat import ChatRequest
from app.enums.api import HTTPStatusCode, RequestKey, ResponseKey
from app.services.chat_service import ChatService


class ChatController:
    """
    Handles incoming FastAPI requests for LLM chat interactions.
    Validates inputs and delegates processing to ChatService.

    Methods:
        chat(request): Handles a synchronous chat request and returns a JSON response.
        stream_chat(request): Handles a streaming chat request and returns a StreamingResponse.
    """

    def __init__(self, service: ChatService):
        """
        Initializes the ChatController with a ChatService instance.

        Args:
            service (ChatService): The underlying service handling agent logic.
        """
        self.service = service

    async def chat(self, request: Request):
        """
        Handles a streaming chat request and returns token-by-token output.

        Args:
            request (Request): The FastAPI request containing user input.

        Returns:
            StreamingResponse: A stream of agent output as plain text.
        """
        try:
            body = ChatRequest(**await request.json())
            user_input = getattr(body, RequestKey.INPUT)
            session_id = getattr(body, RequestKey.SESSION_ID)

            if not user_input:
                return JSONResponse(
                    {ResponseKey.ERROR: f"Missing '{RequestKey.INPUT}' field"},
                    status_code=HTTPStatusCode.BAD_REQUEST,
                )

            stream = self.service.chat(user_input, session_id)
            return StreamingResponse(
                stream, media_type="text/plain", status_code=HTTPStatusCode.OK
            )

        except ValueError as ve:
            return JSONResponse(
                {ResponseKey.ERROR: str(ve)}, status_code=HTTPStatusCode.BAD_REQUEST
            )

        except Exception as e:
            return JSONResponse(
                {ResponseKey.ERROR: "Internal server error"},
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
            )
