"""
tool_planner.py

Smart tool planner for dispatching tool calls based on user intent.
Supports rule-based routing or LLM-based multi-step planning.

Author: Ricardo Arcifa
Updated: 2025-08-06
"""
# app/lib/tools/tool_planner.py
# add near the top
import re
import logging
logger = logging.getLogger("agent")

import json
from typing import Dict, List, Optional
from venv import logger

from jinja2 import Template

from app.config import planner_template
from app.enums.tools import ToolName
from app.lib.model.model_core import ModelCore
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

    def __init__(self, use_llm: bool = True):
        """
        Args:
            use_llm (bool): If True, use LLM to generate a tool plan; otherwise use rule-based matching.
        """
        self.use_llm = use_llm
        self.registry = TOOL_FUNCTIONS
        self.model = ModelCore() if use_llm else None

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
    def _llm_plan(self, user_input: str) -> list[dict]:
        """
        Uses an LLM to generate a tool plan as a JSON list of steps.
        Robust to prose/code-fenced outputs.
        """
        prompt = Template(planner_template).render(
            input=user_input,
            available_tools=", ".join(self.registry.keys()),
        )
        raw = self.model.run(prompt)
        plan = _parse_json_array(raw)

        # validate against registry and ensure 'input' is present when missing
        valid_names = set(self.registry.keys())
        cleaned: list[dict] = []
        for step in plan:
            if not isinstance(step, dict):
                continue
            tool = step.get("tool")
            if tool in valid_names:
                cleaned.append({
                    "tool": tool,
                    "input": step.get("input", user_input),
                })

        logger.info("Tool plan: %s", cleaned)
        return cleaned

    
@staticmethod
def _parse_json_array(raw: str) -> list[dict]:
    """
    Accepts messy LLM output and returns a JSON array (or []).
    Handles prose, code fences, and extracts the first [] block.
    """
    if not raw or not raw.strip():
        logger.warning("Planner returned empty content")
        return []

    s = raw.strip()

    # strip ``` or ```json fences if present
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.IGNORECASE | re.MULTILINE).strip()

    # fast path
    try:
        val = json.loads(s)
        return val if isinstance(val, list) else []
    except Exception:
        pass

    # extract first JSON array anywhere in the string
    m = re.search(r"\[(?:.|\s)*\]", s)
    if m:
        try:
            val = json.loads(m.group(0))
            return val if isinstance(val, list) else []
        except Exception:
            logger.exception("Planner JSON extraction failed on matched array")

    logger.warning("Planner produced non-JSON output (truncated): %r", s[:300])
    return []
