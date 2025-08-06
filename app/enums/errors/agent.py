"""
agent.py

Defines standardized error type enums for categorizing agent-related failures.
Used to label and return consistent error codes across agent pipeline components.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from enum import StrEnum


class AgentErrorType(StrEnum):
    """
    Enum representing different categories of agent errors.

    Attributes:
        AGENT_RUN: Error during synchronous agent run.
        AGENT_BACKGROUND_EVAL: Error during background evaluation.
    """

    AGENT_RUN = "[agent/run] error"
    AGENT_BACKGROUND_EVAL = "[agent/_background_eval] error"
    AGENT_SANITIZE_INPUT = "[agent_utils/sanitize_input] error"
    AGENT_BUILD_CONTEXT = "[agent_utils/build_context] error"
    AGENT_RENDER_PROMPT = "[agent_utils/render_prompt] error"
    AGENT_STREAM_CAPTURE = "[agent_utils/stream_with_capture] error"
