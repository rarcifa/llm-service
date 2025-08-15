"""Module documentation for `app/domain/tools/impl/step_executor.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import logging
from typing import Any, Dict, List

from app.common.error_handling import error_boundary
from app.domain.tools.base.step_executor_base import StepExecutorBase
from app.registry.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)
try:
    from jsonschema import ValidationError, validate
except Exception:
    validate = None
    ValidationError = Exception


@error_boundary(map_to=None, reraise=False, default=False, log=False)
def _args_valid(schema: Dict[str, Any] | None, args: Dict[str, Any]) -> bool:
    """Summary of `_args_valid`.

    Args:
        schema (Dict[str, Any] | None): Description of schema.
        args (Dict[str, Any]): Description of args.

    Returns:
        bool: Description of return value.

    """
    if validate and isinstance(schema, dict):
        validate(instance=args, schema=schema)
    return True


class StepExecutorImpl(StepExecutorBase):
    """Summary of `StepExecutorImpl`.

    Attributes:
        registry: Description of `registry`.
    """

    def __init__(self):
        """Summary of `__init__`.

        Args:
            self: Description of self.

        Returns:
            Any: Description of return value.

        """
        self.registry = ToolRegistry()

    def execute(self, plan: List[Dict[str, Any]]) -> str:
        """Summary of `execute`.

        Args:
            self: Description of self.
            plan (List[Dict[str, Any]]): Description of plan.

        Returns:
            str: Description of return value.

        """
        result: str = ""
        for step in plan:
            tool = step.get("tool")
            spec = self.registry.get(tool)
            if not spec:
                continue
            args = step.get("args", {})
            if not args and "input" in step:
                args = {"input": step["input"]}
            if not _args_valid(spec.args_schema, args):
                logger.warning("Args validation failed for %s", tool)
                continue
            out = spec.handler(**args) if args else spec.handler(result or "")
            if isinstance(out, list):
                out = "\n".join(map(str, out))
            result = out or ""
        return str(result)
