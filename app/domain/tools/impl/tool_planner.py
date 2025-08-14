"""Smart tool planner for dispatching tool calls based on user intent."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from jinja2 import Template

from app.common.decorators.errors import catch_and_log_errors
from app.config import CFG
from app.domain.provider.impl.ollama_provider import Provider
from app.domain.tools.base.tool_planner_base import ToolPlannerBase
from app.registry.prompt_registry import PromptRegistry
from app.registry.tool_registry import TOOL_FUNCTIONS

logger = logging.getLogger("agent")


class ToolPlanner(ToolPlannerBase):
    """
    Returns a sequence of tool steps to execute, enabling multi-step reasoning.

    Each step:
        {"tool": "search_docs", "input": "Find something"}
    """

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.registry = TOOL_FUNCTIONS
        self.provider = Provider() if use_llm else None

    def route(self, user_input: str) -> List[Dict[str, Any]]:
        if self.use_llm:
            return self._llm_plan(user_input)
        step = self._rule_based_tool(user_input)
        return [step] if step else []

    def _rule_based_tool(self, user_input: str) -> Optional[Dict[str, str]]:
        lowered = user_input.lower()
        if "search" in lowered or "find" in lowered:
            return {"tool": "search_docs", "input": user_input}
        if "summarize" in lowered:
            return {"tool": "summarize", "input": user_input}
        if "calculate" in lowered or "math" in lowered:
            return {"tool": "calculator", "input": user_input}
        return None

    @catch_and_log_errors(default_return=[])
    def _llm_plan(self, user_input: str) -> List[Dict[str, str]]:
        registry = PromptRegistry(base_path=str(CFG.prompts.registry_dir))
        planner_prompt = registry.get("agent/planner")
        planner_template = planner_prompt["template"]
        prompt = Template(planner_template).render(
            input=user_input,
            available_tools=", ".join(self.registry.keys()),
        )
        raw = self.provider.run(prompt)  # type: ignore[union-attr]
        plan = self._parse_json_array(raw)

        valid_names = set(self.registry.keys())
        cleaned: List[Dict[str, str]] = []
        for step in plan:
            if not isinstance(step, dict):
                continue
            tool = step.get("tool")
            if tool in valid_names:
                input_val = step.get("input", None)
                if input_val is None or (isinstance(input_val, str) and not input_val.strip()):
                    # leave input absent so StepExecutor uses the previous tool's output
                    cleaned.append({"tool": tool})
                else:
                    cleaned.append({"tool": tool, "input": input_val})

        logger.info("Tool plan: %s", cleaned)
        return cleaned

    @staticmethod
    def _parse_json_array(raw: str) -> List[Dict[str, Any]]:
        """Accept messy LLM output and return a JSON array (or [])."""
        if not raw or not raw.strip():
            logger.warning("Planner returned empty content")
            return []

        s = raw.strip()
        # Strip fences
        if s.startswith("```"):
            s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.IGNORECASE | re.MULTILINE).strip()

        # Fast path
        try:
            val = json.loads(s)
            return val if isinstance(val, list) else []
        except Exception:
            pass

        # Extract first JSON array anywhere
        m = re.search(r"\[(?:.|\s)*\]", s)
        if m:
            try:
                val = json.loads(m.group(0))
                return val if isinstance(val, list) else []
            except Exception:
                logger.exception("Planner JSON extraction failed on matched array")

        logger.warning("Planner produced non-JSON output (truncated): %r", s[:300])
        return []
