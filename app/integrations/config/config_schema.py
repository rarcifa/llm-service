"""Module documentation for `app/db/schemas/config.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-16.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# -------- Core config --------

class Paths(BaseModel):
    data_dir: str
    logs_dir: str
    prompt_dir: str
    vector_store_dir: str
    feedback_path: str


class ModelCfg(BaseModel):
    provider: str
    model_id: str
    temperature: float
    max_tokens: int


class ModelsCfg(BaseModel):
    main: ModelCfg
    eval: ModelCfg


class MemoryCfg(BaseModel):
    enabled: bool
    backend: str
    collection_name: str
    window_size: int
    expiry_minutes: int
    persistence_dir: Optional[str] = None


class RetrievalEmbeddings(BaseModel):
    provider: str
    model: str
    dim: int
    device: Optional[str] = None


class RetrievalCfg(BaseModel):
    enabled: bool
    backend: str
    docs_path: str
    chunk_size: int
    include_ext: List[str]
    embeddings: RetrievalEmbeddings


class EvalThresholds(BaseModel):
    helpfulness_min: int
    grounding_min: float  # 0..1


class EvalCfg(BaseModel):
    enabled: bool
    thresholds: EvalThresholds
    evals: List[Dict[str, Any]]


class ToolSpec(BaseModel):
    name: str
    module: str
    class_: Optional[str] = Field(None, alias="class")
    entrypoint: Optional[str] = None
    description: str = ""
    when_to_use: str = ""
    args_schema: Dict[str, Any] = Field(default_factory=dict)


class ToolsCfg(BaseModel):
    enabled: bool
    registry: List[ToolSpec]


class PluginSpec(BaseModel):
    name: str
    module: str
    class_: str = Field(..., alias="class")
    enabled: bool


class LoggingCfg(BaseModel):
    level: str
    format: str
    sinks: List[Dict[str, Any]]


# -------- Prompts (inline, no registry/files needed) --------

class PromptItem(BaseModel):
    id: str
    name: str
    version: str
    template_name: str
    template: str
    placeholders: List[str]


class PromptsAgent(BaseModel):
    system: PromptItem
    qa: PromptItem
    planner: PromptItem


class PromptsEval(BaseModel):
    helpfulness: PromptItem
    grounding: PromptItem


class PromptsReviewer(BaseModel):
    relevance: PromptItem


class PromptsCfg(BaseModel):
    # Keep these optional for backward-compat with any leftover code,
    # but primary access should be via agent/eval/reviewer.
    registry_dir: Optional[str] = None
    files: Optional[List[str]] = None
    agent: PromptsAgent
    eval: PromptsEval
    reviewer: PromptsReviewer


# -------- Top-level --------

class ConfigRequest(BaseModel):
    name: str
    version: str
    description: Optional[str] = ""
    paths: Paths
    models: ModelsCfg
    memory: MemoryCfg
    retrieval: RetrievalCfg
    eval: EvalCfg
    prompts: PromptsCfg
    tools: ToolsCfg
    plugins: List[PluginSpec]
    logging: LoggingCfg
