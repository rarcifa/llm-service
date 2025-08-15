"""Module documentation for `app/registry/tool_registry.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from app.config import config
from app.registry.base_registry import BaseRegistry, RegistryError


@dataclass(frozen=True)
class LoadedTool:
    """Summary of `LoadedTool`."""

    name: str
    description: str
    when_to_use: str
    args_schema: Dict[str, Any]
    handler: Callable[..., Any]


class ToolRegistry(BaseRegistry[LoadedTool]):
    """Summary of `ToolRegistry`."""

    def _load_all(self) -> None:
        """Summary of `_load_all`.

        Args:
            self: Description of self.

        """
        tools_cfg = getattr(config, "tools", None)
        if not tools_cfg or not getattr(tools_cfg, "enabled", False):
            self.cache.clear()
            return
        reg = getattr(tools_cfg, "registry", [])
        for t in reg:
            handler = self._resolve_callable(
                t.module,
                getattr(t, "class_", None),
                getattr(t, "entrypoint", None) or "run",
            )
            self.cache[t.name] = LoadedTool(
                name=t.name,
                description=t.description,
                when_to_use=t.when_to_use,
                args_schema=t.args_schema,
                handler=handler,
            )

    def _resolve_callable(
        self, module: str, class_: Optional[str], entrypoint: str
    ) -> Callable[..., Any]:
        """Summary of `_resolve_callable`.

        Args:
            self: Description of self.
            module (str): Description of module.
            class_ (Optional[str]): Description of class_.
            entrypoint (str): Description of entrypoint.

        Returns:
            Callable[..., Any]: Description of return value.

        Raises:
            RegistryError: Condition when this is raised.

        """
        mod = importlib.import_module(module)
        if class_:
            cls = getattr(mod, class_)
            instance = cls()
            fn = getattr(instance, entrypoint, None) or getattr(
                instance, "__call__", None
            )
        else:
            fn = getattr(mod, entrypoint, None)
        if not callable(fn):
            qual = f"{module}.{(class_ + '.' if class_ else '')}{entrypoint}"
            raise RegistryError(f"{qual} is not callable")
        return fn

    def _card(self, item: LoadedTool) -> dict:
        """Summary of `_card`.

        Args:
            self: Description of self.
            item (LoadedTool): Description of item.

        Returns:
            dict: Description of return value.

        """
        return {
            "name": item.name,
            "description": item.description,
            "when_to_use": item.when_to_use,
            "args_schema": item.args_schema,
        }

    def execute(self, name: str, /, **kwargs) -> Any:
        """Summary of `execute`.

        Args:
            self: Description of self.
            name (str): Description of name.
            kwargs: Description of kwargs.

        Returns:
            Any: Description of return value.

        """
        tool = self.get(name)
        return tool.handler(**kwargs)
