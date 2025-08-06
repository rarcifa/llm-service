"""
manifest.py

Defines configuration keys used in agent manifest files (e.g., YAML or JSON)
that describe agent capabilities, components, and thresholds.

These keys are used to standardize access to structured config blocks across
evaluation, memory, model selection, and other runtime features.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from enum import StrEnum


class ManifestConfigKey(StrEnum):
    """
    Enum for top-level manifest configuration keys.

    Attributes:
        MODEL: Key for model settings (e.g., model name, provider).
        EVAL: Key for evaluation settings (e.g., enablement, thresholds).
        RETRIEVAL: Key for document retrieval settings.
        MEMORY: Key for memory configuration (e.g., window size, backend).
        THRESHOLDS: Key for evaluation threshold definitions.
    """

    MODEL = "model"
    EVAL = "eval"
    RETRIEVAL = "retrieval"
    MEMORY = "memory"
    THRESHOLDS = "thresholds"
