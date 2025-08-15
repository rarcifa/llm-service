import logging
from typing import Any, Dict, List
from app.domain.tools.base.step_executor_base import StepExecutorBase
from app.common.error_handling import error_boundary
from app.registry.tool_registry import ToolRegistry  # ⬅️ add

logger = logging.getLogger(__name__)

try:
    from jsonschema import validate, ValidationError
except Exception:
    validate = None
    ValidationError = Exception  # fallback

@error_boundary(map_to=None, reraise=False, default=False, log=False)
def _args_valid(schema: Dict[str, Any] | None, args: Dict[str, Any]) -> bool:
    if validate and isinstance(schema, dict):
        validate(instance=args, schema=schema)  # raises on invalid
    return True

class StepExecutorImpl(StepExecutorBase):
    def __init__(self):
        self.registry = ToolRegistry()

    def execute(self, plan: List[Dict[str, Any]]) -> str:
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
