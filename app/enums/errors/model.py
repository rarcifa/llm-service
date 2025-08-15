"""Module documentation for `app/enums/errors/model.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from enum import StrEnum


class ModelErrorType(StrEnum):
    """Summary of `ModelErrorType`."""

    RUN_MODEL_OUTPUT = "[model/run_model_output] error"
    STREAM_WITH_HTTP = "[model/stream_with_http] error"
    STREAM_WITH_CLI = "[model/stream_with_cli] error"
    VERIFY_PROMPT_VARS = "[model/verify_prompt_variables] error"
