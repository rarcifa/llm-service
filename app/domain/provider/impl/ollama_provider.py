# app/domain/provider/impl/ollama_provider.py
from typing import Generator

from app.config import CFG
from app.domain.provider.base.provider_base import ProviderBase
from app.domain.provider.impl.ollama_client import OllamaClient
from app.enums.prompts import RoleKey


class Provider(ProviderBase):
    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def run(self, prompt: str) -> str:
        return self.client.generate(
            model=CFG.models.main.model_id,
            prompt=prompt,
            options={
                "temperature": CFG.models.main.temperature,
                "num_ctx": CFG.models.main.max_tokens,
            },
        )

    def stream(self, prompt: str) -> Generator[str, None, None]:
        messages = [{"role": RoleKey.USER, "content": prompt}]
        return self.client.chat_stream(
            model=CFG.models.main.model_id,
            messages=messages,
            options={
                "temperature": CFG.models.main.temperature,
                "num_ctx": CFG.models.main.max_tokens,
            },
        )
