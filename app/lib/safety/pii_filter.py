"""
pii_filter.py

Uses Microsoft Presidio to detect and anonymize sensitive personally identifiable information (PII)
from user input. Currently supports redaction of phone numbers, emails, credit cards, and SSNs.

This module helps ensure privacy compliance and protects against data leaks.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

from app.lib.utils.decorators.errors import catch_and_log_errors

# === Initialize Presidio engines ===
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


@catch_and_log_errors(default_return="[PII REDACTION FAILED]")
def redact_pii(text: str) -> str:
    """
    Redacts sensitive PII (phone, email, credit card, SSN) from the given text.

    Args:
        text (str): The raw input text potentially containing PII.

    Returns:
        str: The redacted/anonymized version of the text.
    """
    # Detect supported PII entities
    results = analyzer.analyze(
        text=text,
        entities=["PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD", "US_SSN"],
        language="en",
    )

    # Anonymize the detected entities
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)
    return anonymized_text.text
