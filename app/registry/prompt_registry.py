"""
prompt_registry.py

Loads, caches, and renders YAML-based prompt templates. Files include:
id, version, placeholders, template (Jinja2), and optional metadata.

Typical usage:
    registry = PromptRegistry(base_path="prompts")
    raw = registry.get("agent/qa")              # dict with id, version, template
    rendered = registry.render("agent/qa", {"name": "Alice", "input": "Hello"})

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from jinja2 import Template

from app.registry.base_registry import BaseRegistry, RegistryError



@dataclass(frozen=True)
class PromptRecord:
    """Parsed prompt file."""
    name: str                     # logical path (e.g., 'agent/qa')
    id: str
    version: str
    template: str
    placeholders: list[str]
    meta: Dict[str, Any]


class PromptRegistry(BaseRegistry[PromptRecord]):
    """
    Manages access to structured YAML prompt templates.

    Attributes:
        base_path (Path): Root directory containing prompt YAML files.
        cache (dict[str, PromptRecord]): In-memory cache of prompts.
    """

    def __init__(self, base_path: str = "prompts") -> None:
        self.base_path = Path(base_path)
        super().__init__()

    # --- Base hooks -------------------------------------------------------------

    def _load_all(self) -> None:
        """
        Walk `base_path` for *.yaml files and load them into the cache.
        Names are relative paths without extension (e.g., 'agent/qa').
        """
        if not self.base_path.exists():
            raise RegistryError(f"Prompt path does not exist: {self.base_path}")

        for yml in self.base_path.rglob("*.yaml"):
            name = yml.relative_to(self.base_path).with_suffix("").as_posix()
            with yml.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            record = PromptRecord(
                name=name,
                id=str(data.get("id", name)),
                version=str(data.get("version", "0")),
                template=str(data.get("template", "")),
                placeholders=list(data.get("placeholders", [])),
                meta={k: v for k, v in data.items() if k not in {"id", "version", "template", "placeholders"}},
            )
            self.cache[name] = record

    def _card(self, item: PromptRecord) -> dict:
        """Metadata card for UIs and diagnostics."""
        return {
            "name": item.name,
            "id": item.id,
            "version": item.version,
            "placeholders": item.placeholders,
            **({"meta": item.meta} if item.meta else {}),
        }

    # --- Prompt-specific API ----------------------------------------------------

    def render(self, name: str, variables: Dict[str, Any]) -> str:
        """
        Render a prompt using Jinja2 with the given variables.

        Args:
            name: Prompt name (e.g., 'agent/qa').
            variables: Dict of variables for the template.

        Returns:
            The rendered prompt string.

        Raises:
            ItemNotFound: If the prompt is not found.
            ValueError: If required placeholders are missing.
        """
        record = self.get(name)
        missing = [k for k in record.placeholders if k not in variables]
        if missing:
            raise ValueError(f"Missing prompt variables: {missing}")
        return Template(record.template).render(**variables)
