"""Module documentation for `app/domain/provider/impl/ollama_client.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Generator, List, Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from app.common.decorators.errors import error_boundary


class OllamaClient:
    """Summary of `OllamaClient`.

    Attributes:
        base_url: Description of `base_url`.
        session: Description of `session`.
        timeout: Description of `timeout`.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:11434", timeout: int = 60):
        """Summary of `__init__`.

        Args:
            self: Description of self.
            base_url (str): Description of base_url, default='http://127.0.0.1:11434'.
            timeout (int): Description of timeout, default=60.

        Returns:
            Any: Description of return value.

        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _post(self, path: str, payload: Dict[str, Any], stream: bool = False):
        """Summary of `_post`.

        Args:
            self: Description of self.
            path (str): Description of path.
            payload (Dict[str, Any]): Description of payload.
            stream (bool): Description of stream, default=False.

        Returns:
            Any: Description of return value.

        """
        return self.session.post(
            f"{self.base_url}{path}", json=payload, timeout=self.timeout, stream=stream
        )

    @error_boundary()
    def _loads_or_none(self, text: str) -> Any:
        """Summary of `_loads_or_none`.

        Args:
            self: Description of self.
            text (str): Description of text.

        Returns:
            Any: Description of return value.

        """
        return json.loads(text)

    def _parse_json_block(self, text: str) -> Any:
        """Summary of `_parse_json_block`.

        Args:
            self: Description of self.
            text (str): Description of text.

        Returns:
            Any: Description of return value.

        Raises:
            ValueError: Condition when this is raised.

        """
        s = (text or "").strip()
        val = self._loads_or_none(s)
        if val is not None:
            return val
        first_obj, last_obj = (s.find("{"), s.rfind("}"))
        first_arr, last_arr = (s.find("["), s.rfind("]"))
        candidate = ""
        if first_obj != -1 and last_obj != -1 and (last_obj > first_obj):
            candidate = s[first_obj : last_obj + 1]
        elif first_arr != -1 and last_arr != -1 and (last_arr > first_arr):
            candidate = s[first_arr : last_arr + 1]
        if candidate:
            val = self._loads_or_none(candidate)
            if val is not None:
                return val
        raise ValueError("Model did not return valid JSON")

    @error_boundary()
    def generate(
        self,
        model: str,
        prompt: str,
        *,
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Summary of `generate`.

        Args:
            self: Description of self.
            model (str): Description of model.
            prompt (str): Description of prompt.
            format (Optional[str]): Description of format, default=None.
            options (Optional[Dict[str, Any]]): Description of options, default=None.
            extra (Optional[Dict[str, Any]]): Description of extra, default=None.

        Returns:
            str: Description of return value.

        """
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

    @error_boundary()
    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        *,
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Summary of `chat`.

        Args:
            self: Description of self.
            model (str): Description of model.
            messages (List[Dict[str, str]]): Description of messages.
            format (Optional[str]): Description of format, default=None.
            options (Optional[Dict[str, Any]]): Description of options, default=None.
            extra (Optional[Dict[str, Any]]): Description of extra, default=None.

        Returns:
            str: Description of return value.

        """
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
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

    @error_boundary()
    def generate_json(
        self,
        model: str,
        prompt: str,
        *,
        options: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Summary of `generate_json`.

        Args:
            self: Description of self.
            model (str): Description of model.
            prompt (str): Description of prompt.
            options (Optional[Dict[str, Any]]): Description of options, default=None.
            extra (Optional[Dict[str, Any]]): Description of extra, default=None.

        Returns:
            Any: Description of return value.

        """
        text = self.generate(model, prompt, format="json", options=options, extra=extra)
        return self._parse_json_block(text)

    @error_boundary()
    def chat_json(
        self,
        model: str,
        messages: List[Dict[str, str]],
        *,
        options: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Summary of `chat_json`.

        Args:
            self: Description of self.
            model (str): Description of model.
            messages (List[Dict[str, str]]): Description of messages.
            options (Optional[Dict[str, Any]]): Description of options, default=None.
            extra (Optional[Dict[str, Any]]): Description of extra, default=None.

        Returns:
            Any: Description of return value.

        """
        text = self.chat(model, messages, format="json", options=options, extra=extra)
        return self._parse_json_block(text)

    def chat_stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        *,
        options: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Generator[str, None, None]:
        """Summary of `chat_stream`.

        Args:
            self: Description of self.
            model (str): Description of model.
            messages (List[Dict[str, str]]): Description of messages.
            options (Optional[Dict[str, Any]]): Description of options, default=None.
            extra (Optional[Dict[str, Any]]): Description of extra, default=None.

        Returns:
            Generator[str, None, None]: Description of return value.

        """
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
                chunk = self._loads_or_none(line)
                if not isinstance(chunk, dict):
                    continue
                yield (chunk.get("message", {}).get("content", "") or "")
