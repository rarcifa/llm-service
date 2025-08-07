"""
config.py

Loads and centralizes all runtime configuration needed for the agent system,
including:
- Prompt templates from modular YAML files
- Manifest-based toggles (eval, retrieval, thresholds, etc.)
- Model selection and memory initialization

This module is imported by various components and provides shared constants.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import yaml

from app.constants.values import MANIFEST_PATH, PROMPT_DIR
from app.enums.eval import EvalConfigKey, RetrievalConfigKey
from app.enums.manifest import ManifestConfigKey
from app.enums.prompts import PromptConfigKey
from app.enums.tools import ToolName
from app.lib.embeddings.embeddings_core import EmbeddingsCore
from app.lib.tools.registries.prompt_registry import PromptRegistry

# === Load and parse manifest.yaml ===
with MANIFEST_PATH.open() as f:
    manifest_cfg = yaml.safe_load(f)

# === Initialize prompt registry ===
prompt_registry = PromptRegistry(PROMPT_DIR)

# === Load modular YAML prompts ===
system = prompt_registry.get("agent/system")
planner = prompt_registry.get("agent/planner")
qa = prompt_registry.get("agent/qa")
helpfulness = prompt_registry.get("eval/helpfulness")
grounding = prompt_registry.get("eval/grounding")
relevance = prompt_registry.get("reviewer/relevance")

# === Extract system prompt values ===
system_template = system[PromptConfigKey.TEMPLATE]

# === Extract planner prompt values ===
planner_template = planner[PromptConfigKey.TEMPLATE]

# === Extract QA prompt details ===
qa_template = qa[PromptConfigKey.TEMPLATE]
qa_template_name = qa[PromptConfigKey.TEMPLATE_NAME]
qa_prompt_version = qa[PromptConfigKey.VERSION]
qa_name = qa[PromptConfigKey.NAME]

# === Eval-specific templates ===
helpfulness_template = helpfulness[PromptConfigKey.TEMPLATE]
grounding_template = grounding[PromptConfigKey.TEMPLATE]
relevance_template = relevance[PromptConfigKey.TEMPLATE]

# === Manifest-based runtime config ===

main_model = manifest_cfg["models"]["main"]["model_id"]
eval_model = manifest_cfg["models"]["eval"]["model_id"]
rag_model = manifest_cfg["models"]["rag"]["model_id"]
embedding_model = manifest_cfg["models"]["embedding"]["model_id"]

main_temperature = manifest_cfg["models"]["main"].get("temperature", 0.3)
main_max_tokens = manifest_cfg["models"]["main"].get("max_tokens", 1024)

chroma_path = manifest_cfg.get("retrieval", {}).get("chroma_path", "data/chroma_db")
context_window = (
    manifest_cfg.get("models", {}).get("main", {}).get("context_window", 1024)
)
top_p = manifest_cfg.get("models", {}).get("main", {}).get("top_p", 0.95)

use_eval = manifest_cfg.get(ManifestConfigKey.EVAL, {}).get(
    EvalConfigKey.ENABLED, False
)
retrieval_enabled = manifest_cfg.get(ManifestConfigKey.RETRIEVAL, {}).get(
    RetrievalConfigKey.ENABLED, False
)
thresholds = manifest_cfg.get(ManifestConfigKey.EVAL, {}).get(
    ManifestConfigKey.THRESHOLDS, {}
)

# === Guardrails ===
guardrail_cfg = manifest_cfg.get("guardrails", {})
input_filters = {
    ToolName.PII_REDACTOR: guardrail_cfg.get("pii_filter", "presidio"),
    ToolName.PROMPT_INJECTION_DETECTOR: guardrail_cfg.get(
        "prompt_injection_detection", "rebuff"
    ),
}
output_filters = guardrail_cfg.get("output_filters", [])

# === Singleton memory manager ===
memory = EmbeddingsCore(manifest_cfg[ManifestConfigKey.MEMORY])
