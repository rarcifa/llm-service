"""Module documentation for `app/domain/safety/utils/pii_filter.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

from app.common.decorators.errors import catch_and_log_errors

_analyzer = AnalyzerEngine()
_anonymizer = AnonymizerEngine()


@catch_and_log_errors(default_return="[PII REDACTION FAILED]")
def redact_pii(text: str) -> str:
    """Summary of `redact_pii`.

    Args:
        text (str): Description of text.

    Returns:
        str: Description of return value.

    """
    results = _analyzer.analyze(
        text=text,
        entities=["PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD", "US_SSN"],
        language="en",
    )
    anonymized = _anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text
