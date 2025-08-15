"""
tool_registry.py

Loads and caches tools declared in configuration. Each tool resolves to a
callable (module function or class method) and exposes metadata.

Typical usage:
    registry = ToolRegistry()
    search = registry.get("search")       # LoadedTool
    result = registry.execute("search", query="AI agents")

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from __future__ import annotations
import importlib
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from app.config import config
from app.registry.base_registry import BaseRegistry, RegistryError


@dataclass(frozen=True)
class LoadedTool:
    """Resolved tool with metadata and a callable handler."""
    name: str
    description: str
    when_to_use: str
    args_schema: Dict[str, Any]
    handler: Callable[..., Any]


class ToolRegistry(BaseRegistry[LoadedTool]):
    """
    Manages access to callable tools declared in configuration.

    Attributes:
        cache (dict[str, LoadedTool]): In-memory cache of tools keyed by name.
    """

    # --- Base hooks -------------------------------------------------------------

    def _load_all(self) -> None:
        """Load all enabled tools from configuration into the cache."""
        tools_cfg = getattr(config, "tools", None)
        if not tools_cfg or not getattr(tools_cfg, "enabled", False):
            self.cache.clear()
            return

        reg = getattr(tools_cfg, "registry", [])
        for t in reg:
            handler = self._resolve_callable(t.module, getattr(t, "class_", None), getattr(t, "entrypoint", None) or "run")
            self.cache[t.name] = LoadedTool(
                name=t.name,
                description=t.description,
                when_to_use=t.when_to_use,
                args_schema=t.args_schema,
                handler=handler,
            )

    def _resolve_callable(self, module: str, class_: Optional[str], entrypoint: str) -> Callable[..., Any]:
        """Dynamically import and resolve the callable for a tool."""
        mod = importlib.import_module(module)
        if class_:
            cls = getattr(mod, class_)
            instance = cls()  # extend for DI as needed
            fn = getattr(instance, entrypoint, None) or getattr(instance, "__call__", None)
        else:
            fn = getattr(mod, entrypoint, None)
        if not callable(fn):
            qual = f"{module}.{class_+'.' if class_ else ''}{entrypoint}"
            raise RegistryError(f"{qual} is not callable")
        return fn

    def _card(self, item: LoadedTool) -> dict:
        """Metadata card for UIs and diagnostics."""
        return {
            "name": item.name,
            "description": item.description,
            "when_to_use": item.when_to_use,
            "args_schema": item.args_schema,
        }

    # --- Tool-specific API ------------------------------------------------------

    def execute(self, name: str, /, **kwargs) -> Any:
        """
        Execute a tool by name with the provided keyword arguments.

        Args:
            name: Tool name.
            **kwargs: Arguments to pass to the tool handler.

        Returns:
            Any: Result from the tool handler.

        Raises:
            ItemNotFound: If the tool is not found.
        """
        tool = self.get(name)
        return tool.handler(**kwargs)
