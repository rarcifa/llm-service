"""Module documentation for `app/domain/tools/impl/tool_planner.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import json
import logging

from app.common.error_handling import error_boundary
from app.config import config
from app.domain.provider.impl.ollama_provider import Provider
from app.domain.tools.base.tool_planner_base import ToolPlannerBase
from app.registry.prompt_registry import PromptRegistry
from app.registry.tool_registry import ToolRegistry

logger = logging.getLogger("agent")


@error_boundary(map_to=None, reraise=False, default=None, log=False)
def _safe_run_json(provider: Provider, prompt: str, temperature: float):
    """Summary of `_safe_run_json`.

    Args:
        provider (Provider): Description of provider.
        prompt (str): Description of prompt.
        temperature (float): Description of temperature.

    Returns:
        Any: Description of return value.

    """
    return provider.run_json(prompt, temperature=temperature)


class ToolPlanner(ToolPlannerBase):
    """Summary of `ToolPlanner`.

    Attributes:
        provider: Description of `provider`.
        registry: Description of `registry`.
        use_llm: Description of `use_llm`.
    """

    MAX_STEPS = 3

    def __init__(self, use_llm: bool = True):
        """Summary of `__init__`.

        Args:
            self: Description of self.
            use_llm (bool): Description of use_llm, default=True.

        Returns:
            Any: Description of return value.

        """
        self.use_llm = use_llm
        self.registry = ToolRegistry()
        self.provider = Provider() if use_llm else None

    def route(self, user_input: str):
        """Summary of `route`.

        Args:
            self: Description of self.
            user_input (str): Description of user_input.

        Returns:
            Any: Description of return value.

        """
        if not self.use_llm:
            return []
        reg = PromptRegistry(base_path=str(config.prompts.registry_dir))
        prompt = reg.render(
            "agent/planner",
            {"input": user_input, "tool_cards": json.dumps(self.registry.cards())},
        )
        raw = _safe_run_json(self.provider, prompt, 0.0)
        if raw is None:
            logger.warning("Planner JSON failed → PASS []")
            return []
        if isinstance(raw, list):
            plan = raw
        elif isinstance(raw, dict):
            plan = [raw]
        elif isinstance(raw, str):
            parsed = _safe_run_json(self.provider, raw, 0.0)
            if isinstance(parsed, list):
                plan = parsed
            elif isinstance(parsed, dict):
                plan = [parsed]
            else:
                logger.warning("Planner returned string but not JSON → PASS []")
                return []
        else:
            logger.warning("Planner returned unsupported type %s → PASS []", type(raw))
            return []
        allowed = set(self.registry.keys())
        cleaned = []
        for step in plan[: self.MAX_STEPS]:
            if not isinstance(step, dict):
                continue
            name = step.get("tool")
            args = step.get("args") or {}
            if isinstance(name, str) and name in allowed and isinstance(args, dict):
                cleaned.append({"tool": name, "args": args})
        return cleaned
