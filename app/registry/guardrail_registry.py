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

from app.domain.safety.utils.hallucination_filter import filter_hallucinations
from app.domain.safety.utils.injection_detector import detect_prompt_injection
from app.domain.safety.utils.pii_filter import redact_pii
from app.domain.safety.utils.profanity_filter import filter_profanity
from app.enums.tools import ToolName

GUARDRAIL_FUNCTIONS: Dict[str, Dict[str, Callable | str]] = {
    ToolName.PROMPT_INJECTION_DETECTOR: {
        "function": detect_prompt_injection,
        "description": "Detects prompt injection attempts using heuristics or patterns.",
    },
    ToolName.PII_REDACTOR: {
        "function": redact_pii,
        "description": "Redacts personally identifiable information (PII) from user input.",
    },
    ToolName.PROFANITY_FILTER: {
        "function": filter_profanity,
        "description": "Censors or replaces profane or inappropriate language in the input.",
    },
    ToolName.HALLUCINATION_BLOCKER: {
        "function": filter_hallucinations,
        "description": "Removes or flags hallucinated content from the model output.",
    },
}
