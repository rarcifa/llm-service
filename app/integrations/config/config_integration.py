"""Module documentation for `app/services/integration/config_integration.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-16.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import httpx

from app.constants.values import APP_CONFIG_NAME, APP_CONFIG_PROFILE, CONFIG_SERVICE_URL, CONFIG_TIMEOUT_SEC
from app.integrations.config.config_schema import ConfigRequest


class ConfigIntegration:
    """Summary of `ConfigIntegration`."""

    def __init__(self) -> None:
        """Summary of `__init__`."""
        self.client = httpx.Client(timeout=CONFIG_TIMEOUT_SEC)

    def load(self) -> ConfigRequest:
        """Summary of `load`.

        Try remote Spring Config Server first; fallback to local manifest.
        """
        url = f"{CONFIG_SERVICE_URL.rstrip('/')}/{APP_CONFIG_NAME}/{APP_CONFIG_PROFILE}"
        resp = self.client.get(url)
        resp.raise_for_status()
        payload = resp.json()

        nested = self._merge_property_sources(payload)
        python_dict = self._spring_to_python_schema(nested)
        return ConfigRequest(**python_dict)


    @staticmethod
    def _merge_property_sources(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Merge Spring 'propertySources' into a single nested dict."""
        def dot_to_nested(d: Dict[str, Any], key: str, value: Any) -> None:
            parts = key.split(".")
            cur = d
            for p in parts[:-1]:
                cur = cur.setdefault(p, {})
            cur[parts[-1]] = value

        merged_flat: Dict[str, Any] = {}
        for ps in payload.get("propertySources", []):
            src: Dict[str, Any] = ps.get("source", {})
            merged_flat.update(src)

        nested: Dict[str, Any] = {}
        for k, v in merged_flat.items():
            dot_to_nested(nested, k, v)
        return nested


    @staticmethod
    def _spring_to_python_schema(nested: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "name": nested.get("app", {}).get("name", ""),
            "version": nested.get("app", {}).get("version", ""),
            "description": nested.get("app", {}).get("description", ""),
        }

        p = nested.get("paths", {})
        out["paths"] = {
            "data_dir": p.get("dataDir"),
            "logs_dir": p.get("logsDir"),
            "prompt_dir": p.get("promptDir"),
            "vector_store_dir": p.get("vectorStoreDir"),
            "feedback_path": p.get("feedbackPath"),
        }

        m = nested.get("models", {})
        def mk_model(mm: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "provider": mm.get("provider"),
                "model_id": mm.get("modelId"),
                "temperature": float(mm.get("temperature", 0.0)),
                "max_tokens": int(mm.get("maxTokens", 1024)),
            }
        out["models"] = {"main": mk_model(m.get("main", {})), "eval": mk_model(m.get("eval", {}))}

        mem = nested.get("memory", {})
        out["memory"] = {
            "enabled": bool(mem.get("enabled", True)),
            "backend": mem.get("backend", "postgres"),
            "collection_name": mem.get("collectionName", "agent_docs"),
            "window_size": int(mem.get("windowSize", 3)),
            "expiry_minutes": int(mem.get("expiryMinutes", 90)),
            "persistence_dir": nested.get("paths", {}).get("vectorStoreDir"),
        }

        ret = nested.get("retrieval", {})
        out["retrieval"] = {
            "enabled": bool(ret.get("enabled", True)),
            "backend": ret.get("backend", "postgres"),
            "docs_path": ret.get("docsPath", "data"),
            "chunk_size": int(ret.get("chunkSize", 300)),
            "include_ext": list(ret.get("includeExt", ["*.txt", "*.md"])),
            "embeddings": {
                "provider": ret.get("embeddings", {}).get("provider"),
                "model": ret.get("embeddings", {}).get("model"),
                "dim": int(ret.get("embeddings", {}).get("dim", 384)),
                "device": ret.get("embeddings", {}).get("device"),
            },
        }

        ev = nested.get("eval", {})
        th = ev.get("thresholds", {})
        out["eval"] = {
            "enabled": bool(ev.get("enabled", True)),
            "thresholds": {
                "helpfulness_min": int(th.get("helpfulnessMin", 3)),
                "grounding_min": float(th.get("groundingMin", 0.9)),
            },
            "evals": list(ev.get("evals", [])),
        }

        # ---------- NEW: nested inline prompts ----------
        def map_item(node: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "id": node.get("id", ""),
                "name": node.get("name", ""),
                "version": node.get("version", "1.0.0"),
                "template_name": node.get("templateName", "default"),
                "template": node.get("template", ""),
                "placeholders": list(node.get("placeholders", [])),
            }

        pr = nested.get("prompts", {})
        agent = pr.get("agent", {})
        evalp = pr.get("eval", {})
        reviewer = pr.get("reviewer", {})

        out["prompts"] = {
            "registry_dir": None,  # optional legacy fields
            "files": None,
            "agent": {
                "system": map_item(agent.get("system", {})),
                "qa": map_item(agent.get("qa", {})),
                "planner": map_item(agent.get("planner", {})),
            },
            "eval": {
                "helpfulness": map_item(evalp.get("helpfulness", {})),
                "grounding": map_item(evalp.get("grounding", {})),
            },
            "reviewer": {
                "relevance": map_item(reviewer.get("relevance", {})),
            },
        }
        # ---------- end prompts ----------

        tools = nested.get("tools", {})
        reg_py: List[Dict[str, Any]] = []
        for t in tools.get("registry", []):
            reg_py.append({
                "name": t.get("name"),
                "module": t.get("module"),
                "class": t.get("className"),
                "entrypoint": t.get("entrypoint", "run"),
                "description": t.get("description", ""),
                "when_to_use": t.get("whenToUse", ""),
                "args_schema": t.get("argsSchema", {}),
            })
        out["tools"] = {"enabled": bool(tools.get("enabled", True)), "registry": reg_py}

        out["plugins"] = list(nested.get("plugins", []))

        lg = nested.get("logging", {})
        out["logging"] = {
            "level": lg.get("level", "info"),
            "format": lg.get("format", "json"),
            "sinks": list(lg.get("sinks", [])),
        }
        return out
