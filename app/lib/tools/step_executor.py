"""
step_executor.py

Executes a sequence of tool steps (multi-step plan).
Each step can optionally use the output of the previous tool as its input.

Used in combination with the ToolPlanner to enable chain-of-thought style reasoning
across multiple tools before invoking the LLM.

Author: Ricardo Arcifa
Created: 2025-08-06
"""

from typing import Callable, Dict, List

from app.lib.utils.decorators.errors import catch_and_log_errors


class StepExecutor:
    """
    Executes a plan of tool steps.

    Each step is a dictionary with:
        - 'tool' (str): the name of a registered tool
        - 'input' (str, optional): input to the tool (if omitted, will use previous output)

    Example input plan:
    [
        {"tool": "search_docs", "input": "Find info about CLM"},
        {"tool": "summarize"}  # input is taken from result of previous step
    ]
    """

    def __init__(self, registry: Dict[str, Dict[str, Callable]]):
        """
        Initializes the step executor.

        Args:
            registry (Dict): A dictionary mapping tool names to metadata,
                             each containing at least a 'function' callable.
        """
        self.registry = registry

    @catch_and_log_errors(default_return="[Tool execution failed]")
    def execute(self, plan: List[Dict[str, str]]) -> str:
        """
        Executes all tool steps in sequence.

        Args:
            plan (List[Dict]): A list of tool steps (see format above).

        Returns:
            str: The output of the final tool in the chain.

        Raises:
            ValueError: If a step is missing a valid tool name or the tool is unregistered.
        """
        result = ""

        for i, step in enumerate(plan):
            tool = step.get("tool")
            input_text = (
                step.get("input") or result
            )  # Use previous output if input is missing

            if not tool:
                raise ValueError(f"Step {i} is missing a 'tool' key.")

            if tool not in self.registry:
                raise ValueError(
                    f"Tool '{tool}' is not registered in the tool registry."
                )

            tool_fn = self.registry[tool]["function"]
            result = tool_fn(input_text)

        return result
