from __future__ import annotations

from app.domain.safety.base.safety_base import DetectorBase
from app.domain.safety.utils.injection_detector import detect_prompt_injection


class InjectionDetectorImpl(DetectorBase):
    """Concrete prompt-injection detector using pattern matching."""

    def detect(self, text: str) -> bool:
        return detect_prompt_injection(text)
