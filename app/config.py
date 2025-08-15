from __future__ import annotations
# app/config.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from app.registry.prompt_registry import PromptRecord, PromptRegistry

MANIFEST_PATH = Path("manifest.yaml")


@dataclass(frozen=True)
class Paths:
    data_dir: Path
    logs_dir: Path
    prompt_dir: Path
    vector_store_dir: Path
    feedback_path: Path


@dataclass(frozen=True)
class ModelCfg:
    provider: str
    model_id: str
    temperature: float
    max_tokens: int


@dataclass(frozen=True)
class MemoryCfg:
    enabled: bool
    backend: str
    collection_name: str
    window_size: int
    expiry_minutes: int
    persistence_dir: Path


@dataclass(frozen=True)
class Models:
    main: ModelCfg
    eval: ModelCfg


@dataclass(frozen=True)
class RetrievalCfg:
    enabled: bool
    backend: str  # NEW: "postgres" | "chroma"
    docs_path: Path
    chunk_size: int
    include_ext: tuple[str, ...]
    embeddings_model: str
    embeddings_provider: str
    embeddings_dim: int  # NEW


@dataclass(frozen=True)
class EvalCfg:
    enabled: bool
    helpfulness_min: int
    grounding_min: int
    evals: tuple[dict, ...]


@dataclass(frozen=True)
class LoggingCfg:
    level: str
    format: str
    sinks: tuple[dict, ...]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    module: str
    # Optional: either supply a class (we'll instantiate it), or omit and use a module function.
    class_: str | None = None
    # Optional: method on the class instance OR function name on the module (defaults to "run").
    entrypoint: str | None = None
    # Optional routing metadata for planner cards:
    description: str = ""
    when_to_use: str = ""
    # Optional JSON Schema for args (validated before execution)
    args_schema: dict = field(default_factory=lambda: {
        "type": "object",
        "properties": {"input": {"type": "string"}},
        "required": [],
        "additionalProperties": True,
    })


@dataclass(frozen=True)
class ToolsCfg:
    enabled: bool
    registry: tuple[ToolSpec, ...]


@dataclass(frozen=True)
class PluginSpec:
    name: str
    module: str
    class_: str
    enabled: bool


@dataclass(frozen=True)
class PromptData:
    name: str
    template: str
    placeholders: tuple[str, ...]
    id: str | None = None
    version: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PromptsCfg:
    registry_dir: Path
    files: tuple[str, ...]
    loaded: dict[str, PromptData]


@dataclass(frozen=True)
class AppCfg:
    name: str
    version: str
    description: str
    paths: Paths
    models: Models
    memory: MemoryCfg
    retrieval: RetrievalCfg
    eval: EvalCfg
    prompts: PromptsCfg
    tools: ToolsCfg
    plugins: tuple[PluginSpec, ...]
    logging: LoggingCfg


def _as_model(cfg: dict, key: str) -> ModelCfg:
    m = cfg["models"][key]
    return ModelCfg(
        provider=m["provider"],
        model_id=m["model_id"],
        temperature=float(m.get("temperature", 0.0)),
        max_tokens=int(m.get("max_tokens", 1024)),
    )


def load_config(path: Path = MANIFEST_PATH) -> AppCfg:
    data = yaml.safe_load(path.read_text())

    # paths
    p = data["paths"]
    paths = Paths(
        data_dir=Path(p["data_dir"]),
        logs_dir=Path(p["logs_dir"]),
        prompt_dir=Path(p["prompt_dir"]),
        vector_store_dir=Path(p["vector_store_dir"]),
        feedback_path=Path(p["feedback_path"]),
    )

    # models
    models = Models(
        main=_as_model(data, "main"),
        eval=_as_model(data, "eval"),
    )

    # memory
    mem = data["memory"]
    memory = MemoryCfg(
        enabled=bool(mem["enabled"]),
        backend=mem["backend"],
        collection_name=mem["collection_name"],
        window_size=int(mem["window_size"]),
        expiry_minutes=int(mem["expiry_minutes"]),
        persistence_dir=paths.vector_store_dir,
    )

    # retrieval
    ret = data["retrieval"]
    retrieval = RetrievalCfg(
        enabled=bool(ret["enabled"]),
        backend=str(ret.get("backend", "postgres")),
        docs_path=Path(ret["docs_path"]),
        chunk_size=int(ret["chunk_size"]),
        include_ext=tuple(ret["include_ext"]),
        embeddings_model=ret["embeddings"]["model"],
        embeddings_provider=ret["embeddings"]["provider"],
        embeddings_dim=int(ret["embeddings"].get("dim", 384)),
    )

    # eval
    ev = data["eval"]
    thresholds = ev["thresholds"]
    eval_cfg = EvalCfg(
        enabled=bool(ev["enabled"]),
        helpfulness_min=int(thresholds["helpfulness_min"]),
        grounding_min=int(thresholds["grounding_min"]),
        evals=tuple(ev["evals"]),
    )

    # prompts
    pr = data["prompts"]
    registry_dir = paths.prompt_dir
    registry = PromptRegistry(base_path=str(registry_dir))
    loaded_prompts: dict[str, PromptData] = {}

    for key in pr["files"]:
        record: PromptRecord = registry.get(key)  # raises ItemNotFound if missing
        loaded_prompts[key] = PromptData(
            name=record.name,
            template=record.template,
            placeholders=tuple(record.placeholders),
            id=record.id,
            version=record.version,
            meta=record.meta,
        )

    prompts = PromptsCfg(
        registry_dir=registry_dir,
        files=tuple(pr["files"]),
        loaded=loaded_prompts,
    )


    # tools
    tl = data["tools"]
    tools = ToolsCfg(
        enabled=bool(tl["enabled"]),
        registry=tuple(
            ToolSpec(
                name=t["name"],
                module=t["module"],
                class_=t.get("class"),                    # optional
                entrypoint=t.get("entrypoint", "run"),    # default "run"
                description=t.get("description", ""),
                when_to_use=t.get("when_to_use", ""),
                args_schema=t.get("args_schema", {
                    "type": "object",
                    "properties": {"input": {"type": "string"}},
                    "required": [],
                    "additionalProperties": True,
                }),
            )
            for t in tl["registry"]
        ),
    )

    # plugins
    plugins = tuple(
        PluginSpec(
            name=pl["name"],
            module=pl["module"],
            class_=pl["class"],
            enabled=bool(pl["enabled"]),
        )
        for pl in data.get("plugins", [])
    )
    
    # logging
    lg = data["logging"]
    logging = LoggingCfg(
        level=lg["level"],
        format=lg["format"],
        sinks=tuple(lg["sinks"]),
    )

    return AppCfg(
        name=data["name"],
        version=data["version"],
        description=data.get("description", ""),
        paths=paths,
        models=models,
        memory=memory,
        retrieval=retrieval,
        eval=eval_cfg,
        prompts=prompts,
        tools=tools,
        plugins=plugins,
        logging=logging,
    )


# Export a singleton for convenience
config = load_config()