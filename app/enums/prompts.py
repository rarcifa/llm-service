"""
prompts.py

Defines enums for:
- Model types
- Evaluation score keys
- JSON serialization keys
- Prompt configuration keys
- Conversation role identifiers

These enums support structured access to commonly used keys across the
agent pipeline: prompt rendering, scoring, logging, persistence, and feedback.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from enum import StrEnum


class ModelType(StrEnum):
    """
    Enum for supported model types.

    Attributes:
        LLAMA3: Refers to the LLaMA3 language model family.
    """

    LLAMA3 = "llama3"


class ScoreKey(StrEnum):
    """
    Enum for evaluation metric keys.

    Attributes:
        HELPFULNESS: Score for helpfulness.
        GROUNDING: Grounding evaluation score.
        HALLUCINATION: Hallucination risk score.
        RATING: Overall rating score.
    """

    HELPFULNESS = "eval.helpfulness"
    GROUNDING = "eval.grounding_score"
    HALLUCINATION = "eval.hallucination_risk"
    RATING = "eval.rating"


class JsonKey(StrEnum):
    """
    Keys used for structured JSON responses and logs.

    Attributes:
        SESSION_ID: Unique session identifier (⚠️ typo: 'session_id' should be fixed).
        RESPONSE_ID: Unique identifier for the model response.
        TRACE_ID: Identifier used for tracing/logging purposes.
        FEEDBACK_ID: ID for human or system feedback record.
        MESSAGE_ID: ID for a message in a conversation.
        RATING: Final human/eval rating.
        STATUS: Status of the response or evaluation.
        INPUT: Original user input.
        RESPONSE: Model's generated response.
    """

    SESSION_ID = "session_id"
    RESPONSE_ID = "response_id"
    TRACE_ID = "trace_id"
    FEEDBACK_ID = "feedback_id"
    MESSAGE_ID = "message_id"
    RATING = "rating"
    STATUS = "status"
    INPUT = "input"
    RESPONSE = "response"


class PromptConfigKey(StrEnum):
    """
    Keys used in prompt configuration and template rendering.

    Attributes:
        TEMPLATE: Full prompt template content.
        TEMPLATE_NAME: Template identifier (e.g., 'qa', 'chat').
        VERSION: Prompt version number or hash.
        NAME: Friendly name for the prompt.
        ID: Unique ID for the prompt instance.
    """

    TEMPLATE = "template"
    TEMPLATE_NAME = "template_name"
    VERSION = "version"
    NAME = "name"
    ID = "id"


class RoleKey(StrEnum):
    """
    Role identifiers used in chat or conversation history.

    Attributes:
        USER: Indicates a user message.
        AGENT: Indicates an agent (model) response.
    """

    USER = "user"
    AGENT = "agent"
