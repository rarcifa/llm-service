# app/domain/safety/utils/pii_filter.py
"""PII redaction with Presidio (pure transform)."""
from __future__ import annotations
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from app.common.decorators.errors import catch_and_log_errors

# Singleton engines (initialized once at import)
_analyzer = AnalyzerEngine()
_anonymizer = AnonymizerEngine()

@catch_and_log_errors(default_return="[PII REDACTION FAILED]")
def redact_pii(text: str) -> str:
    """Redact PHONE, EMAIL, CREDIT_CARD, US_SSN from `text`."""
    results = _analyzer.analyze(
        text=text,
        entities=["PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD", "US_SSN"],
        language="en",
    )
    anonymized = _anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized.text
