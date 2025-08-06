"""
model.py

Defines ModelErrorType enum used to categorize and trace errors
that occur during evaluation steps such as grounding scoring,
helpfulness judging, hallucination detection, and final rating.

This improves observability, logging, and debugging when
integrated with error decorators and tracing.

Author: Ricardo Arcifa
Created: 2025-08-06
"""

from enum import StrEnum


class ModelErrorType(StrEnum):
    """
    Enum representing error types related to model interactions.

    Attributes:
        RUN_MODEL_OUTPUT: Error during blocking model execution via CLI.
        STREAM_WITH_HTTP: Failure while streaming model output over HTTP.
        STREAM_WITH_CLI: Failure while streaming model output via CLI.
        VERIFY_PROMPT_VARS: Missing or unresolved template variables.
    """

    RUN_MODEL_OUTPUT = "[model/run_model_output] error"
    STREAM_WITH_HTTP = "[model/stream_with_http] error"
    STREAM_WITH_CLI = "[model/stream_with_cli] error"
    VERIFY_PROMPT_VARS = "[model/verify_prompt_variables] error"
