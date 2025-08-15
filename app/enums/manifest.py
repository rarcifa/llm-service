"""Module documentation for `app/enums/manifest.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from enum import StrEnum


class ManifestConfigKey(StrEnum):
    """Summary of `ManifestConfigKey`."""

    MODEL = "model"
    EVAL = "eval"
    RETRIEVAL = "retrieval"
    MEMORY = "memory"
    THRESHOLDS = "thresholds"
