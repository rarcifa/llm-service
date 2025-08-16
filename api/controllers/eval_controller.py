"""Module documentation for `api/controllers/eval_controller.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations


from fastapi import Request
from fastapi.responses import JSONResponse

from api.controllers.eval_schema import EvalRequest
from app.enums.api import HTTPStatusCode, ResponseKey
from app.services.eval_service import EvalService


class EvalController:
    """Summary of `EvalController`.

    Attributes:
        service: Description of `service`.
    """

    def __init__(self, service: EvalService):
        """Summary of `__init__`.

        Args:
            self: Description of self.
            service (ChatService): Description of service.

        Returns:
            Any: Description of return value.

        """
        self.service = service

    async def run(self, request: Request):
        """Summary of `chat`.

        Args:
            self: Description of self.
            request (Request): Description of request.

        Returns:
            Any: Description of return value.

        """
        try:
            body = EvalRequest(**await request.json())

            result = self.service.run(
                filtered_input=body.filtered_input,
                response=body.response,
                retrieved_docs=body.retrieved_docs,
                response_id=body.response_id,
                message_id=body.message_id,
                session_id=body.session_id,
                rendered_prompt=body.rendered_prompt,
                raw_input=body.raw_input,
                conversation_history=body.conversation_history,
            )
            return JSONResponse(result, status_code=HTTPStatusCode.OK)

        except ValueError as ve:
            return JSONResponse(
                {ResponseKey.ERROR: str(ve)}, status_code=HTTPStatusCode.BAD_REQUEST
            )
        except Exception:
            return JSONResponse(
                {ResponseKey.ERROR: "Internal server error"},
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
            )
