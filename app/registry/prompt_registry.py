"""Module documentation for `app/registry/prompt_registry.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml
from jinja2 import Template

from app.registry.base_registry import BaseRegistry, RegistryError


@dataclass(frozen=True)
class PromptRecord:
    """Summary of `PromptRecord`."""

    name: str
    id: str
    version: str
    template: str
    placeholders: list[str]
    meta: Dict[str, Any]


class PromptRegistry(BaseRegistry[PromptRecord]):
    """Summary of `PromptRegistry`.

    Attributes:
        base_path: Description of `base_path`.
    """

    def __init__(self, base_path: str = "prompts") -> None:
        """Summary of `__init__`.

        Args:
            self: Description of self.
            base_path (str): Description of base_path, default='prompts'.

        """
        self.base_path = Path(base_path)
        super().__init__()

    def _load_all(self) -> None:
        """Summary of `_load_all`.

        Args:
            self: Description of self.

        Raises:
            RegistryError: Condition when this is raised.

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
                meta={
                    k: v
                    for k, v in data.items()
                    if k not in {"id", "version", "template", "placeholders"}
                },
            )
            self.cache[name] = record

    def _card(self, item: PromptRecord) -> dict:
        """Summary of `_card`.

        Args:
            self: Description of self.
            item (PromptRecord): Description of item.

        Returns:
            dict: Description of return value.

        """
        return {
            "name": item.name,
            "id": item.id,
            "version": item.version,
            "placeholders": item.placeholders,
            **({"meta": item.meta} if item.meta else {}),
        }

    def render(self, name: str, variables: Dict[str, Any]) -> str:
        """Summary of `render`.

        Args:
            self: Description of self.
            name (str): Description of name.
            variables (Dict[str, Any]): Description of variables.

        Returns:
            str: Description of return value.

        Raises:
            ValueError: Condition when this is raised.

        """
        record = self.get(name)
        missing = [k for k in record.placeholders if k not in variables]
        if missing:
            raise ValueError(f"Missing prompt variables: {missing}")
        return Template(record.template).render(**variables)
