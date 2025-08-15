from __future__ import annotations

from typing import Any, Dict, Generator, List, Optional
import json
import requests
from requests.adapters import HTTPAdapter, Retry
from app.common.error_handling import error_boundary  # ⬅️ add


class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    # -------- core helpers ---------------------------------------------------

    def _post(self, path: str, payload: Dict[str, Any], stream: bool = False):
        return self.session.post(
            f"{self.base_url}{path}", json=payload, timeout=self.timeout, stream=stream
        )

    @error_boundary(map_to=None, reraise=False, default=None, log=False)
    def _loads_or_none(self, text: str) -> Any:
        # centralized swallow; returns None on any json error
        return json.loads(text)

    def _parse_json_block(self, text: str) -> Any:
        """
        Best-effort JSON parse (no inline try/except):
        1) direct parse
        2) extract the first {...} or [...] block and parse that
        """
        s = (text or "").strip()
        val = self._loads_or_none(s)
        if val is not None:
            return val

        # Heuristic extraction (no try/except here)
        first_obj, last_obj = s.find("{"), s.rfind("}")
        first_arr, last_arr = s.find("["), s.rfind("]")

        candidate = ""
        if first_obj != -1 and last_obj != -1 and last_obj > first_obj:
            candidate = s[first_obj : last_obj + 1]
        elif first_arr != -1 and last_arr != -1 and last_arr > first_arr:
            candidate = s[first_arr : last_arr + 1]

        if candidate:
            val = self._loads_or_none(candidate)
            if val is not None:
                return val

        # If we get here, keep the central mapping at the public boundary
        raise ValueError("Model did not return valid JSON")

    # -------- non-stream APIs -----------------------------------------------

    @error_boundary(message="OllamaClient.generate failed")
    def generate(
        self,
        model: str,
        prompt: str,
        *,
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload: Dict[str, Any] = {"model": model, "prompt": prompt, "stream": False}
        if format:
            payload["format"] = format
        if options:
            payload["options"] = options
        if extra:
            payload.update(extra)
        r = self._post("/api/generate", payload)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")

    @error_boundary(message="OllamaClient.chat failed")
    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        *,
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload: Dict[str, Any] = {"model": model, "messages": messages, "stream": False}
        if format:
            payload["format"] = format
        if options:
            payload["options"] = options
        if extra:
            payload.update(extra)
        r = self._post("/api/chat", payload)
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")

    # -------- JSON-mode convenience wrappers --------------------------------

    @error_boundary(message="OllamaClient.generate_json failed")
    def generate_json(
        self,
        model: str,
        prompt: str,
        *,
        options: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Any:
        text = self.generate(model, prompt, format="json", options=options, extra=extra)
        return self._parse_json_block(text)

    @error_boundary(message="OllamaClient.chat_json failed")
    def chat_json(
        self,
        model: str,
        messages: List[Dict[str, str]],
        *,
        options: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Any:
        text = self.chat(model, messages, format="json", options=options, extra=extra)
        return self._parse_json_block(text)

    # -------- streaming (avoid for JSON mode) --------------------------------

    # NOTE: generator; leave undecorated unless you add a generator-aware wrapper
    def chat_stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        *,
        options: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Generator[str, None, None]:
        payload: Dict[str, Any] = {"model": model, "messages": messages, "stream": True}
        if options:
            payload["options"] = options
        if extra:
            payload.update(extra)

        with self._post("/api/chat", payload, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                chunk = self._loads_or_none(line)  # swallow malformed lines
                if not isinstance(chunk, dict):
                    continue
                yield chunk.get("message", {}).get("content", "") or ""
