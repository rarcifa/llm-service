# domain/provider/base/provider_base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generator, List, Dict, Any, Union

Message = Dict[str, str]  # {"role": "system|user|assistant", "content": "..."}

class ProviderBase(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def stream(self, messages: List[Message], **kwargs: Any) -> Generator[str, None, None]:
        """Yield text chunks from the model for the given chat messages."""
        raise NotImplementedError
