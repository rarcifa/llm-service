"""Module documentation for `app/domain/provider/impl/ollama_provider.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from typing import Any, Dict, Generator, List

from app.common.error_handling import error_boundary
from app.config import config
from app.domain.provider.base.provider_base import ProviderBase
from app.domain.provider.impl.ollama_client import OllamaClient
from app.enums.prompts import RoleKey


class Provider(ProviderBase):
    """Summary of `Provider`.

    Attributes:
        client: Description of `client`.
    """

    def __init__(self, client: OllamaClient | None = None):
        """Summary of `__init__`.

        Args:
            self: Description of self.
            client (OllamaClient | None): Description of client, default=None.

        Returns:
            Any: Description of return value.

        """
        self.client = client or OllamaClient()

    @error_boundary(message="Provider.run failed")
    def run(self, prompt: str) -> str:
        """Summary of `run`.

        Args:
            self: Description of self.
            prompt (str): Description of prompt.

        Returns:
            str: Description of return value.

        """
        return self.client.generate(
            model=config.models.main.model_id,
            prompt=prompt,
            options={
                "temperature": config.models.main.temperature,
                "num_ctx": config.models.main.max_tokens,
            },
        )

    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Summary of `stream`.

        Args:
            self: Description of self.
            prompt (str): Description of prompt.

        Returns:
            Generator[str, None, None]: Description of return value.

        """
        messages = [{"role": RoleKey.USER, "content": prompt}]
        return self.client.chat_stream(
            model=config.models.main.model_id,
            messages=messages,
            options={
                "temperature": config.models.main.temperature,
                "num_ctx": config.models.main.max_tokens,
            },
        )

    @error_boundary(message="Provider.run_json failed")
    def run_json(self, prompt: str, *, temperature: float | None = None) -> Any:
        """Summary of `run_json`.

        Args:
            self: Description of self.
            prompt (str): Description of prompt.
            temperature (float | None): Description of temperature, default=None.

        Returns:
            Any: Description of return value.

        """
        temp = (
            config.models.main.temperature
            if temperature is None
            else float(temperature)
        )
        return self.client.generate_json(
            model=config.models.main.model_id,
            prompt=prompt,
            options={"temperature": temp, "num_ctx": config.models.main.max_tokens},
        )

    @error_boundary(message="Provider.chat failed")
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Summary of `chat`.

        Args:
            self: Description of self.
            messages (List[Dict[str, str]]): Description of messages.

        Returns:
            str: Description of return value.

        """
        return self.client.chat(
            model=config.models.main.model_id,
            messages=messages,
            options={
                "temperature": config.models.main.temperature,
                "num_ctx": config.models.main.max_tokens,
            },
        )

    @error_boundary(message="Provider.chat_json failed")
    def chat_json(
        self, messages: List[Dict[str, str]], *, temperature: float | None = None
    ) -> Any:
        """Summary of `chat_json`.

        Args:
            self: Description of self.
            messages (List[Dict[str, str]]): Description of messages.
            temperature (float | None): Description of temperature, default=None.

        Returns:
            Any: Description of return value.

        """
        temp = (
            config.models.main.temperature
            if temperature is None
            else float(temperature)
        )
        return self.client.chat_json(
            model=config.models.main.model_id,
            messages=messages,
            options={"temperature": temp, "num_ctx": config.models.main.max_tokens},
        )
