from typing import Any, Generator, List, Dict
from app.common.error_handling import error_boundary  # ⬅️ add

from app.config import config
from app.domain.provider.base.provider_base import ProviderBase
from app.domain.provider.impl.ollama_client import OllamaClient
from app.enums.prompts import RoleKey


class Provider(ProviderBase):
    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    # ---------- plain text ----------
    @error_boundary(message="Provider.run failed")
    def run(self, prompt: str) -> str:
        return self.client.generate(
            model=config.models.main.model_id,
            prompt=prompt,
            options={
                "temperature": config.models.main.temperature,
                "num_ctx": config.models.main.max_tokens,
            },
        )

    # NOTE: generator; leave undecorated unless you add a generator-aware wrapper
    def stream(self, prompt: str) -> Generator[str, None, None]:
        messages = [{"role": RoleKey.USER, "content": prompt}]
        return self.client.chat_stream(
            model=config.models.main.model_id,
            messages=messages,
            options={
                "temperature": config.models.main.temperature,
                "num_ctx": config.models.main.max_tokens,
            },
        )

    # ---------- JSON-mode helpers ----------
    @error_boundary(message="Provider.run_json failed")
    def run_json(self, prompt: str, *, temperature: float | None = None) -> Any:
        temp = config.models.main.temperature if temperature is None else float(temperature)
        return self.client.generate_json(
            model=config.models.main.model_id,
            prompt=prompt,
            options={"temperature": temp, "num_ctx": config.models.main.max_tokens},
        )

    @error_boundary(message="Provider.chat failed")
    def chat(self, messages: List[Dict[str, str]]) -> str:
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
        temp = config.models.main.temperature if temperature is None else float(temperature)
        return self.client.chat_json(
            model=config.models.main.model_id,
            messages=messages,
            options={"temperature": temp, "num_ctx": config.models.main.max_tokens},
        )
