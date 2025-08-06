"""
prompt_registry.py

Provides an interface to load, cache, and render YAML-based prompt templates.
Each prompt file contains metadata (id, version, placeholders, template),
and supports dynamic rendering via Jinja2.

Typical usage:
    registry = PromptRegistry()
    raw = registry.get("agent/qa")
    rendered = registry.render("agent/qa", {"name": "Alice", "input": "Hello"})

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from pathlib import Path

import yaml
from jinja2 import Template


class PromptRegistry:
    """
    Manages access to prompt templates stored in structured YAML files.

    Attributes:
        base_path (str): Root directory containing prompt YAML files.
        cache (dict): In-memory cache of loaded prompts.
    """

    def __init__(self, base_path: str = "prompts"):
        """
        Initializes the prompt registry.

        Args:
            base_path (str, optional): Directory where YAML files are located.
                Defaults to "prompts".
        """
        self.base_path = Path(base_path)
        self.cache = {}

    def load(self, path: str) -> dict:
        """
        Loads a YAML file (e.g., 'agent/qa') and caches the result.

        Args:
            path (str): Relative path without `.yaml` extension.

        Returns:
            dict: Parsed prompt file containing template, placeholders, etc.
        """
        full_path = self.base_path / f"{path}.yaml"
        if path not in self.cache:
            with full_path.open() as f:
                self.cache[path] = yaml.safe_load(f)
        return self.cache[path]

    def get(self, path: str) -> dict:
        """
        Returns the raw YAML prompt metadata.

        Args:
            path (str): Path to the YAML prompt file.

        Returns:
            dict: Prompt data including id, version, template, placeholders.
        """
        return self.load(path)

    def render(self, path: str, variables: dict) -> str:
        """
        Renders the prompt using Jinja2 with the given variables.

        Args:
            path (str): YAML prompt path (e.g., 'agent/qa').
            variables (dict): Variables to inject into the Jinja2 template.

        Returns:
            str: The rendered prompt string.

        Raises:
            ValueError: If required placeholders are missing from `variables`.
        """
        prompt = self.load(path)
        template_str = prompt["template"]
        required = prompt.get("placeholders", [])
        missing = [k for k in required if k not in variables]

        if missing:
            raise ValueError(f"Missing prompt variables: {missing}")

        return Template(template_str).render(**variables)
