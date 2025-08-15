"""Agent utility functions (pure, function-only).

- Input sanitization with safety filters
- Prompt rendering with Jinja2
- Streaming capture wrapper

Author: Ricardo Arcifa
Created: 2025-02-03
"""
from __future__ import annotations


from typing import Any, Callable, Generator, List

from jinja2 import Template

from app.common.decorators.errors import catch_and_log_errors
from app.config import config
from app.domain.provider.utils.provider_utils import verify_prompt_variables
from app.domain.safety.utils.injection_detector import detect_prompt_injection
from app.domain.safety.utils.pii_filter import redact_pii
from app.domain.safety.utils.profanity_filter import filter_profanity
from app.enums.errors.agent import AgentErrorType
from app.enums.prompts import PromptConfigKey
from app.enums.tools import ToolKey, ToolName


@catch_and_log_errors(default_return={"error": AgentErrorType.AGENT_SANITIZE_INPUT})
def sanitize_io(user_input: str) -> str:
    """Sanitize and normalize user input (PII redaction + profanity filtering)."""
    if detect_prompt_injection(user_input):
        raise ValueError("Prompt injection detected.")
    
    safe_input = redact_pii(user_input)
    filtered = filter_profanity(safe_input)
    return filtered or user_input.strip()


@catch_and_log_errors(default_return={"error": AgentErrorType.AGENT_RENDER_PROMPT})
def render_prompt(filtered_input: str, context_chunks: List[str]) -> str:
    """Render a Jinja2 prompt using input and retrieved context."""

    # In the new config, prompt templates live in config.prompts.registry_dir.
    # You’d typically use PromptRegistry to load them — here assuming you want
    # the QA prompt (agent/qa) and its `name` placeholder.
    from app.registry.prompt_registry import PromptRegistry

    reg = PromptRegistry(base_path=str(config.prompts.registry_dir))
    qa_record = reg.get("agent/qa")  # returns PromptRecord

    qa_name = qa_record.name or "Agent"
    qa_template = qa_record.template  # this is the old qa_prompt["template"]


    missing = verify_prompt_variables(
        qa_template,
        {PromptConfigKey.NAME: qa_name, "context": "...", "input": filtered_input},
    )
    if missing:
        raise ValueError(f"Unresolved prompt variables: {missing}")

    prompt = Template(qa_template).render(
        name=qa_name,
        context="\n".join(context_chunks),
        input=filtered_input,
    )
    if "{{" in prompt or "}}" in prompt:
        raise ValueError("Unresolved placeholders in rendered prompt.")
    return prompt


@catch_and_log_errors(default_return={"error": AgentErrorType.AGENT_STREAM_CAPTURE})
def stream_with_capture(
    stream: Generator[str, None, None],
    on_complete: Callable[[str], Any] | None = None,
) -> Generator[str, None, None]:
    """Wrap a token/chunk generator to capture full output while streaming."""
    buffer: List[str] = []

    def generator() -> Generator[str, None, None]:
        for chunk in stream:
            buffer.append(chunk)
            yield chunk
        full_output = "".join(buffer)
        if on_complete:
            on_complete(full_output)

    return generator()