"""
agent_utils.py

Core utility functions for agent operation:
- Input sanitization with safety filters
- Retrieval-augmented context building
- Prompt rendering with Jinja2
- Conversation persistence to DB and memory

Each function is decorated with automatic error logging and default fallback
values using `@catch_and_log_errors`.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import uuid
from typing import Optional

from jinja2 import Template

from app.config import input_filters, memory, qa_name, qa_template, retrieval_enabled
from app.db.repositories.session_repository import get_session_repo
from app.enums.errors.agent import AgentErrorType
from app.enums.prompts import PromptConfigKey, RoleKey
from app.enums.tools import ToolKey, ToolName
from app.lib.model.model_utils import verify_prompt_variables
from app.lib.safety.injection_detector import detect_prompt_injection
from app.lib.tools.registries.guardrail_registry import GUARDRAIL_FUNCTIONS
from app.lib.tools.registries.tool_registry import TOOL_FUNCTIONS
from app.lib.utils.decorators.errors import catch_and_log_errors


@catch_and_log_errors(default_return={"error": AgentErrorType.AGENT_SANITIZE_INPUT})
def sanitize_input(user_input: str) -> str:
    """
    Applies input sanitization by detecting injection, redacting PII, and filtering profanity.

    Args:
        user_input (str): Raw user input.

    Returns:
        str: Cleaned and safe user input for downstream processing.

    Raises:
        ValueError: If prompt injection is detected.
    """
    if detect_prompt_injection(user_input):
        raise ValueError("Prompt injection detected.")

    # Lookup PII filter from manifest
    pii_tool = GUARDRAIL_FUNCTIONS[input_filters[ToolName.PII_REDACTOR]][
        ToolKey.FUNCTION
    ]

    # Always use fixed profanity filter — since it's post-PII cleaning
    profanity_tool = GUARDRAIL_FUNCTIONS[ToolName.PROFANITY_FILTER][ToolKey.FUNCTION]

    safe_input = pii_tool(user_input)
    filtered = profanity_tool(safe_input)

    return filtered or user_input.strip()


@catch_and_log_errors(default_return={"error": AgentErrorType.AGENT_BUILD_CONTEXT})
def build_context(filtered_input: str) -> list[str]:
    """
    Builds context for the prompt using memory and optional document retrieval.

    Args:
        filtered_input (str): Sanitized user input.

    Returns:
        list[str]: A list of strings representing relevant context chunks.
    """
    context_chunks = memory.retrieve_context(filtered_input)

    if retrieval_enabled:
        docs = TOOL_FUNCTIONS[ToolName.SEARCH_DOCS][ToolKey.FUNCTION](filtered_input)
        context_chunks += docs

    return context_chunks


@catch_and_log_errors(default_return={"error": AgentErrorType.AGENT_RENDER_PROMPT})
def render_prompt(filtered_input: str, context_chunks: list[str]) -> str:
    """
    Renders a Jinja2-based prompt using the input and retrieved context.

    Args:
        filtered_input (str): Sanitized input to insert in the prompt.
        context_chunks (list[str]): List of strings providing supporting context.

    Returns:
        str: The fully rendered prompt string.

    Raises:
        ValueError: If unresolved template variables or placeholders exist.
    """
    # Verify all required keys are present in the prompt template
    missing = verify_prompt_variables(
        qa_template,
        {PromptConfigKey.NAME: qa_name, "context": "...", "input": filtered_input},
    )
    if missing:
        raise ValueError(f"Unresolved prompt variables: {missing}")

    # Render the Jinja2 template
    prompt = Template(qa_template).render(
        name=qa_name,
        context="\n".join(context_chunks),
        input=filtered_input,
    )

    # Detect if any Jinja placeholders remain unresolved
    if "{{" in prompt or "}}" in prompt:
        raise ValueError("Unresolved placeholders in rendered prompt.")

    return prompt


def persist_conversation(
    session_id: str,
    user_input: str,
    response: str,
    tokens_used: Optional[int] = None,
    metadata: Optional[dict] = None,
) -> None:
    """
    Persists the user/agent conversation into both long-term DB and memory.

    Args:
        session_id (str): Unique identifier for the session.
        user_input (str): Original user message.
        response (str): Agent's response to the user.
    """
    with get_session_repo() as repo:
        repo.get_or_create_session(session_id)
        repo.store_message(
            session_id=session_id,
            role=RoleKey.USER,
            content=user_input,
            message_id=uuid.uuid4(),
            tokens_used=tokens_used,
            metadata=metadata,
        )
        repo.store_message(
            session_id=session_id,
            role=RoleKey.AGENT,
            content=response.strip(),
            message_id=uuid.uuid4(),
            tokens_used=tokens_used,
            metadata=metadata,
        )

    memory.store_interaction(user_input, response)


from typing import Any, Callable, Generator, Optional


@catch_and_log_errors(default_return={"error": AgentErrorType.AGENT_STREAM_CAPTURE})
def stream_with_capture(
    stream: Generator[str, None, None],
    on_complete: Callable[[str], Any] = None,
) -> Generator[str, None, None]:
    """
    Streams a generator of string chunks while capturing the full output for later use.

    This is useful when you want to both:
    1. Yield streaming tokens to the client in real-time
    2. Reconstruct the full response afterward (e.g., for saving to DB or eval)

    Args:
        stream (Generator[str, None, None]): The original token or chunk generator (e.g., from LLM).
        on_complete (Callable[[str], Any], optional): A callback to run after streaming ends.
            Receives the full concatenated response as input.

    Returns:
        Generator[str, None, None]: A generator that yields the same chunks as `stream`,
        while also triggering `on_complete` with the final full output once finished.
    """
    buffer = []

    def generator():
        for chunk in stream:
            buffer.append(chunk)
            yield chunk

        full_output = "".join(buffer)

        if on_complete:
            on_complete(full_output)

    return generator()
