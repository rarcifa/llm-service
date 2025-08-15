"""Module documentation for `app/enums/errors/agent.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from enum import StrEnum


class AgentErrorType(StrEnum):
    """Summary of `AgentErrorType`."""

    AGENT_RUN = "[agent/run] error"
    AGENT_BACKGROUND_EVAL = "[agent/_background_eval] error"
    AGENT_SANITIZE_INPUT = "[agent_utils/sanitize_input] error"
    AGENT_BUILD_CONTEXT = "[agent_utils/build_context] error"
    AGENT_RENDER_PROMPT = "[agent_utils/render_prompt] error"
    AGENT_STREAM_CAPTURE = "[agent_utils/stream_with_capture] error"
