# app/config.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

from app.domain.embeddings.impl.embeddings_impl import EmbeddingsImpl
from app.domain.memory.impl.chroma_memory import MemoryImpl

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
class Models:
    main: ModelCfg
    eval: ModelCfg

@dataclass(frozen=True)
class RetrievalCfg:
    enabled: bool
    docs_path: Path
    chunk_size: int
    include_ext: tuple[str, ...]
    embeddings_model: str
    embeddings_provider: str

@dataclass(frozen=True)
class GuardrailsCfg:
    input_prompt_injection_patterns: tuple[str, ...]
    input_profanity_list: tuple[str, ...]
    output_filters: tuple[dict, ...]

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
    class_: str

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
class PromptsCfg:
    registry_dir: Path
    files: tuple[str, ...]

@dataclass(frozen=True)
class AppCfg:
    name: str
    version: str
    description: str
    paths: Paths
    models: Models
    memory: MemoryCfg
    retrieval: RetrievalCfg
    guardrails: GuardrailsCfg
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
    vector_Store = EmbeddingsImpl(path=mem["docs_path"],)
    memory = MemoryImpl(
        store=vector_Store,
        collection_name=mem["collection_name"],
        window_size=3,  
    )

    # retrieval
    ret = data["retrieval"]
    retrieval = RetrievalCfg(
        enabled=bool(ret["enabled"]),
        docs_path=Path(ret["docs_path"]),
        chunk_size=int(ret["chunk_size"]),
        include_ext=tuple(ret["include_ext"]),
        embeddings_model=ret["embeddings"]["model"],
        embeddings_provider=ret["embeddings"]["provider"],
    )

    # guardrails
    gr = data["guardrails"]
    input_filters = gr.get("input_filters", {})
    guardrails = GuardrailsCfg(
        input_prompt_injection_patterns=tuple(input_filters.get("prompt_injection_patterns", [])),
        input_profanity_list=tuple(input_filters.get("profanity_list", [])),
        output_filters=tuple(gr.get("output_filters", [])),
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
    prompts = PromptsCfg(
        registry_dir=paths.prompt_dir,
        files=tuple(pr["files"]),
    )

    # tools
    tl = data["tools"]
    tools = ToolsCfg(
        enabled=bool(tl["enabled"]),
        registry=tuple(
            ToolSpec(name=t["name"], module=t["module"], class_=t["class"])
            for t in tl["registry"]
        ),
    )

    # plugins
    plugins = tuple(
        PluginSpec(
            name=pl["name"], module=pl["module"], class_=pl["class"], enabled=bool(pl["enabled"])
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
        guardrails=guardrails,
        eval=eval_cfg,
        prompts=prompts,
        tools=tools,
        plugins=plugins,
        logging=logging,
    )

# Export a singleton for convenience
CFG = load_config()
