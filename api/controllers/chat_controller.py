"""Module documentation for `api/controllers/chat_controller.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.db.schemas.chat import ChatRequest
from app.enums.api import HTTPStatusCode, RequestKey, ResponseKey
from app.services.chat_service import ChatService


class ChatController:
    """Summary of `ChatController`.

    Attributes:
        service: Description of `service`.
    """

    def __init__(self, service: ChatService):
        """Summary of `__init__`.

        Args:
            self: Description of self.
            service (ChatService): Description of service.

        Returns:
            Any: Description of return value.

        """
        self.service = service

    async def chat(self, request: Request):
        """Summary of `chat`.

        Args:
            self: Description of self.
            request (Request): Description of request.

        Returns:
            Any: Description of return value.

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
