# app/orchestrator.py
from importlib import import_module
from dataclasses import dataclass
from typing import Any

from app.config import CFG
from app.registry.prompt_registry import PromptRegistry
from app.registry.tool_registry import ToolRegistry
from app.registry.guardrail_registry import GuardrailRegistry
from app.services.memory import MemoryImpl  # your impl
from app.services.embeddings import EmbeddingsImpl  # your impl

@dataclass
class Orchestrator:
    prompts: PromptRegistry
    tools: ToolRegistry
    guardrails: GuardrailRegistry
    memory: Any
    embeddings: Any
    plugins: dict[str, Any]

    @classmethod
    def init(cls) -> "Orchestrator":
        # Prompts
        pr = PromptRegistry(base_path=str(CFG.prompts.registry_dir))
        for file_key in CFG.prompts.files:
            pr.load(file_key)  # cache

        # Guardrails
        gr = GuardrailRegistry()
        gr.register_input_patterns(CFG.guardrails.input_prompt_injection_patterns)
        gr.register_profanity(CFG.guardrails.input_profanity_list)
        for f in CFG.guardrails.output_filters:
            gr.register_output_filter(f)

        # Embeddings / Memory
        embeddings = EmbeddingsImpl(path=str(CFG.paths.vector_store_dir))
        memory = MemoryImpl(
            store=embeddings,
            collection_name=CFG.memory.collection_name,
            window_size=CFG.memory.window_size,
        )

        # Tools
        tr = ToolRegistry()
        if CFG.tools.enabled:
            for spec in CFG.tools.registry:
                mod = import_module(spec.module)
                cls_ = getattr(mod, spec.class_)
                tr.register(spec.name, cls_(embeddings=embeddings, memory=memory, config=CFG))

        # Plugins (domains)
        plugins: dict[str, Any] = {}
        for pl in CFG.plugins:
            if not pl.enabled:
                continue
            mod = import_module(pl.module)
            cls_ = getattr(mod, pl.class_)
            plugins[pl.name] = cls_(prompts=pr, tools=tr, guardrails=gr, memory=memory, config=CFG)

        return cls(
            prompts=pr,
            tools=tr,
            guardrails=gr,
            memory=memory,
            embeddings=embeddings,
            plugins=plugins,
        )

    def get_domain(self, name: str):
        return self.plugins[name]
