"""Module documentation for `api/routes/eval_router.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from fastapi import APIRouter, Depends, Request

from api.controllers.eval_controller import EvalController
from app.services.eval_service import EvalService

router = APIRouter(prefix="/eval", tags=["Eval"])


def get_eval_controller():
    """Summary of `get_eval_controller`.

    Args:
        (no arguments)

    Returns:
        Any: Description of return value.

    """
    return EvalController(EvalService())


@router.post("", summary="Run evaluation on an agent response")
async def eval_route(
    request: Request, controller: EvalController = Depends(get_eval_controller)
):
    """Summary of `eval_route`.

    Args:
        request (Request): Description of request.
        controller (EvalController): Description of controller, default=Depends(get_eval_controller).

    Returns:
        Any: Description of return value.

    """
    return await controller.run(request)
