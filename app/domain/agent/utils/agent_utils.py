"""Module documentation for `app/domain/agent/utils/agent_utils.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

import uuid
from typing import Any, Callable, Generator, List, Optional

from jinja2 import Template

from app.common.decorators.errors import error_boundary
from app.common.utils.encoding import sha256
from app.config import config
from app.constants.errors import (
    AGENT_PERSIST,
    AGENT_RENDER_PROMPT,
    AGENT_SANITIZE_INPUT,
    AGENT_STREAM_CAPTURE,
)
from app.db.repositories.pgvector_repository import get_pgvector_repo
from app.db.repositories.session_repository import get_session_repo
from app.domain.provider.utils.provider_utils import verify_prompt_variables
from app.domain.retrieval.utils.embeddings_utils import get_cached_embedding
from app.domain.safety.utils.injection_detector import detect_prompt_injection
from app.domain.safety.utils.pii_filter import redact_pii
from app.domain.safety.utils.profanity_filter import filter_profanity
from app.enums.prompts import PromptConfigKey, RoleKey
from app.enums.tools import ToolKey, ToolName
from app.enums.vector import DistanceMetric


@error_boundary(default_return={"error": AGENT_SANITIZE_INPUT})
def sanitize_io(user_input: str) -> str:
    """Summary of `sanitize_io`.

    Args:
        user_input (str): Description of user_input.

    Returns:
        str: Description of return value.

    Raises:
        ValueError: Condition when this is raised.

    """
    if detect_prompt_injection(user_input):
        raise ValueError("Prompt injection detected.")
    safe_input = redact_pii(user_input)
    filtered = filter_profanity(safe_input)
    return filtered or user_input.strip()


@error_boundary(default_return={"error": AGENT_RENDER_PROMPT})
def render_prompt(filtered_input: str, context_chunks: List[str]) -> str:
    """Summary of `render_prompt`.

    Args:
        filtered_input (str): Description of filtered_input.
        context_chunks (List[str]): Description of context_chunks.

    Returns:
        str: Description of return value.

    Raises:
        ValueError: Condition when this is raised.

    """
    from app.registry.prompt_registry import PromptRegistry

    reg = PromptRegistry(base_path=str(config.prompts.registry_dir))
    qa_record = reg.get("agent/qa")
    qa_name = qa_record.name or "Agent"
    qa_template = qa_record.template
    missing = verify_prompt_variables(
        qa_template,
        {PromptConfigKey.NAME: qa_name, "context": "...", "input": filtered_input},
    )
    if missing:
        raise ValueError(f"Unresolved prompt variables: {missing}")
    prompt = Template(qa_template).render(
        name=qa_name, context="\n".join(context_chunks), input=filtered_input
    )
    if "{{" in prompt or "}}" in prompt:
        raise ValueError("Unresolved placeholders in rendered prompt.")
    return prompt


@error_boundary(default_return={"error": AGENT_STREAM_CAPTURE})
def stream_with_capture(
    stream: Generator[str, None, None], on_complete: Callable[[str], Any] | None = None
) -> Generator[str, None, None]:
    """Summary of `stream_with_capture`.

    Args:
        stream (Generator[str, None, None]): Description of stream.
        on_complete (Callable[[str], Any] | None): Description of on_complete, default=None.

    Returns:
        Generator[str, None, None]: Description of return value.

    """
    buffer: List[str] = []
    for chunk in stream:
        buffer.append(chunk)
        yield chunk
    full_output = "".join(buffer)
    if on_complete:
        on_complete(full_output)


@error_boundary(default_return={"error": AGENT_PERSIST})
def persist_conversation(
    *,
    session_id: str,
    user_input: str,
    response: str,
    tokens_used: Optional[int] = None,
    metadata: Optional[dict] = None,
) -> None:
    """Summary of `persist_conversation`.

    Args:
        session_id (str): Description of session_id.
        user_input (str): Description of user_input.
        response (str): Description of response.
        tokens_used (Optional[int]): Description of tokens_used, default=None.
        metadata (Optional[dict]): Description of metadata, default=None.

    """
    with get_session_repo() as repo:
        repo.get_or_create_session(session_id)
        repo.store_message(
            session_id=session_id,
            role=RoleKey.USER,
            content=user_input,
            message_id=str(uuid.uuid4()),
            tokens_used=tokens_used,
            metadata=metadata,
        )
        repo.store_message(
            session_id=session_id,
            role=RoleKey.AGENT,
            content=response.strip(),
            message_id=str(uuid.uuid4()),
            tokens_used=tokens_used,
            metadata=metadata,
        )
    emb = get_cached_embedding(response)
    with get_pgvector_repo(distance=DistanceMetric.COSINE) as vrepo:
        vrepo.upsert(
            session_id=session_id,
            collection=config.memory.collection_name,
            embedding=emb,
            document=response,
            metadata={"session_id": session_id, **(metadata or {})},
            content_sha256=sha256(response),
        )
