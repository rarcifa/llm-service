"""
tool_planner.py

Smart tool planner for dispatching tool calls based on user intent.
Supports rule-based routing or LLM-based multi-step planning.

Author: Ricardo Arcifa
Updated: 2025-08-06
"""

import json
from typing import Dict, List, Optional

from jinja2 import Template

from app.config import planner_template
from app.enums.tools import ToolName
from app.lib.model.model_runner import ModelRunner
from app.lib.tools.registries.tool_registry import TOOL_FUNCTIONS
from app.lib.utils.decorators.errors import catch_and_log_errors


class ToolPlanner:
    """
    ToolPlanner returns a sequence of tool steps to execute,
    enabling multi-step reasoning with optional LLM-based planning.

    Each step follows this structure:
    {
        "tool": "search_docs",
        "input": "Find something"
    }
    """

    def __init__(self, use_llm: bool = False):
        """
        Args:
            use_llm (bool): If True, use LLM to generate a tool plan; otherwise use rule-based matching.
        """
        self.use_llm = use_llm
        self.registry = TOOL_FUNCTIONS
        self.model = ModelRunner() if use_llm else None

    def route(self, user_input: str) -> List[Dict[str, str]]:
        """
        Generates a tool plan from the user input.

        Returns:
            List[Dict[str, str]]: A list of tool steps (each a dict with 'tool' and optional 'input').
        """
        if self.use_llm:
            return self._llm_plan(user_input)

        # fallback: single-step rule-based routing
        step = self._rule_based_tool(user_input)
        return [step] if step else []

    def _rule_based_tool(self, user_input: str) -> Optional[Dict[str, str]]:
        """
        Matches keywords in input to known tools.

        Returns:
            Optional[Dict[str, str]]: One step with 'tool' and 'input', or None
        """
        lowered = user_input.lower()
        if "search" in lowered or "find" in lowered:
            return {"tool": ToolName.SEARCH_DOCS.value, "input": user_input}
        if "summarize" in lowered:
            return {"tool": ToolName.SUMMARIZE.value, "input": user_input}
        if "calculate" in lowered or "math" in lowered:
            return {"tool": ToolName.CALCULATOR.value, "input": user_input}
        return None

    @catch_and_log_errors(default_return=[])
    def _llm_plan(self, user_input: str) -> List[Dict[str, str]]:
        """
        Uses an LLM to generate a tool plan as a JSON list of steps.

        Returns:
            List[Dict[str, str]]: A multi-step plan.
        """
        prompt = Template(planner_template).render(
            input=user_input,
            available_tools=", ".join(self.registry.keys()),
        )

        raw = self.model.run(prompt)
        return json.loads(raw)
