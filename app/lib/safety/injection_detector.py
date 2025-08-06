"""
injection_detector.py

Implements simple pattern-based detection for prompt injection attempts.
This module scans user input for suspicious patterns commonly used to manipulate LLM behavior.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import re

from app.constants.values import INJECTION_PATTERNS
from app.lib.utils.decorators.errors import catch_and_log_errors


@catch_and_log_errors(default_return=False)
def detect_prompt_injection(text: str) -> bool:
    """
    Checks if the input text contains known prompt injection patterns.

    Args:
        text (str): The user input to scan.

    Returns:
        bool: True if an injection pattern is detected; False otherwise.
    """
    for pattern in INJECTION_PATTERNS:
        # Perform case-insensitive regex match against known patterns
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False
