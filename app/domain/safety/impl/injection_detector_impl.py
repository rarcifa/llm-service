"""Module documentation for `app/domain/safety/impl/injection_detector_impl.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from app.domain.safety.base.safety_base import DetectorBase
from app.domain.safety.utils.injection_detector import detect_prompt_injection


class InjectionDetectorImpl(DetectorBase):
    """Summary of `InjectionDetectorImpl`."""

    def detect(self, text: str) -> bool:
        """Summary of `detect`.

        Args:
            self: Description of self.
            text (str): Description of text.

        Returns:
            bool: Description of return value.

        """
        return detect_prompt_injection(text)
