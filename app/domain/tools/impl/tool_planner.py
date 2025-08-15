import json, logging
from jinja2 import Template
from app.domain.provider.impl.ollama_provider import Provider
from app.domain.tools.base.tool_planner_base import ToolPlannerBase
from app.registry.prompt_registry import PromptRegistry
from app.config import config
from app.registry.tool_registry import ToolRegistry
from app.common.error_handling import error_boundary  # ⬅️ add

logger = logging.getLogger("agent")

@error_boundary(map_to=None, reraise=False, default=None, log=False)
def _safe_run_json(provider: Provider, prompt: str, temperature: float):
    return provider.run_json(prompt, temperature=temperature)

class ToolPlanner(ToolPlannerBase):
    MAX_STEPS = 3

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.registry = ToolRegistry()
        self.provider = Provider() if use_llm else None

    def route(self, user_input: str):
        if not self.use_llm:
            return []

        reg = PromptRegistry(base_path=str(config.prompts.registry_dir))
        prompt = reg.render(
            "agent/planner",
            {
                "input": user_input,
                "tool_cards": json.dumps(self.registry.cards())
            },
        )
        raw = _safe_run_json(self.provider, prompt, 0.0)
        if raw is None:
            logger.warning("Planner JSON failed → PASS []")
            return []

        # normalize to a list of steps
        if isinstance(raw, list):
            plan = raw
        elif isinstance(raw, dict):
            plan = [raw]
        elif isinstance(raw, str):
            parsed = _safe_run_json(  # reuse safe JSON load via provider path
                self.provider, raw, 0.0
            )
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
