from __future__ import annotations

from typing import Any, Callable, Dict, List

from app.common.decorators.errors import catch_and_log_errors
from app.domain.tools.base.step_executor_base import StepExecutorBase


class StepExecutorImpl(StepExecutorBase):
    """
    Executes a plan of tool steps.

    Each step is a dictionary with:
        - 'tool' (str): the name of a registered tool
        - 'input' (str, optional): input to the tool (defaults to previous output)
    """

    def __init__(self, registry: Dict[str, Dict[str, Callable]]):
        self.registry = registry

    @catch_and_log_errors(default_return="[Tool execution failed]")
    def execute(self, plan: List[Dict[str, Any]]) -> str:
        result: Any = ""

        for i, step in enumerate(plan):
            tool = step.get("tool")
            input_text = step.get("input") if step.get("input") is not None else result

            if not tool:
                raise ValueError(f"Step {i} is missing a 'tool' key.")

            if tool not in self.registry:
                raise ValueError(
                    f"Tool '{tool}' is not registered in the tool registry."
                )

            tool_fn = self.registry[tool]["function"]
            # Execute
            out = tool_fn(input_text)

            # Normalize output for chaining (strings are kept; lists joined)
            if isinstance(out, list):
                out = "\n".join(map(str, out))
            elif out is None:
                out = ""

            result = out

        return str(result)
