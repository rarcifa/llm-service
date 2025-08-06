"""
model.py

Defines configuration keys related to model setup and selection,
used in agent manifests and runtime configuration.

This enum allows standardized access to model parameters across services.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from enum import StrEnum


class ModelConfigKey(StrEnum):
    """
    Enum for model-specific configuration keys.

    Attributes:
        MODEL_ID: The identifier or name of the model to use (e.g., "mistral", "gpt-4").
    """

    MODEL_ID = "model_id"
