# app/domain/provider/ollama_client.py
from __future__ import annotations
from typing import Generator, List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter, Retry

class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def generate(self, model: str, prompt: str, **kwargs) -> str:
        payload = {"model": model, "prompt": prompt, "stream": False, **kwargs}
        r = self.session.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")

    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        payload = {"model": model, "messages": messages, "stream": False, **kwargs}
        r = self.session.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")

    def chat_stream(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        payload = {"model": model, "messages": messages, "stream": True, **kwargs}
        with self.session.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                # Each line is a JSON object with partial message content
                try:
                    chunk = requests.models.complexjson.loads(line)
                    yield chunk.get("message", {}).get("content", "") or ""
                except Exception:
                    continue
