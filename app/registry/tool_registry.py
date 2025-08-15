from __future__ import annotations
import importlib
from dataclasses import dataclass
from typing import Any, Callable, Dict
from app.config import CFG

@dataclass(frozen=True)
class LoadedTool:
    name: str
    description: str
    when_to_use: str
    args_schema: Dict[str, Any]
    handler: Callable[..., Any]

def _resolve_callable(module: str, class_: str | None, entrypoint: str) -> Callable[..., Any]:
    mod = importlib.import_module(module)
    if class_:
        cls = getattr(mod, class_)
        instance = cls()  # extend here if you want DI
        fn = getattr(instance, entrypoint, None) or getattr(instance, "__call__", None)
        if not callable(fn):
            raise AttributeError(f"{module}.{class_}.{entrypoint} is not callable")
        return fn
    # module-level function
    fn = getattr(mod, entrypoint)
    if not callable(fn):
        raise AttributeError(f"{module}.{entrypoint} is not callable")
    return fn

def load_tools_from_manifest() -> Dict[str, LoadedTool]:
    if not CFG.tools.enabled:
        return {}
    out: Dict[str, LoadedTool] = {}
    for t in CFG.tools.registry:
        handler = _resolve_callable(t.module, t.class_, t.entrypoint or "run")
        out[t.name] = LoadedTool(
            name=t.name,
            description=t.description,
            when_to_use=t.when_to_use,
            args_schema=t.args_schema,
            handler=handler,
        )
    return out

def build_tool_cards(registry: Dict[str, LoadedTool]) -> str:
    import json
    cards = [{
        "name": r.name,
        "description": r.description,
        "when_to_use": r.when_to_use,
        "args_schema": r.args_schema,
    } for r in registry.values()]
    return json.dumps(cards, ensure_ascii=False)
