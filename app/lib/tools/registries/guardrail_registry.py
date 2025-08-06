"""
guardrail_registry.py

Contains built-in safety and sanitation tools that are automatically applied
during preprocessing in the agent pipeline.

These are NOT selectable via the ToolPlanner. They serve as universal filters
for protecting user privacy, content safety, and prompt injection prevention.

Author: Ricardo Arcifa
Created: 2025-08-06
"""

from typing import Callable, Dict

from app.lib.safety.injection_detector import detect_prompt_injection
from app.lib.safety.pii_filter import redact_pii
from app.lib.safety.profanity_filter import filter_profanity

GUARDRAIL_FUNCTIONS: Dict[str, Dict[str, Callable | str]] = {
    "prompt_injection_detector": {
        "function": detect_prompt_injection,
        "description": "Detects prompt injection attempts using heuristics or patterns.",
    },
    "pii_redactor": {
        "function": redact_pii,
        "description": "Redacts personally identifiable information (PII) from user input.",
    },
    "profanity_filter": {
        "function": filter_profanity,
        "description": "Censors or replaces profane or inappropriate language in the input.",
    },
}
