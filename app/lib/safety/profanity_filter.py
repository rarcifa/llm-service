"""
profanity_filter.py

Implements a profanity filter by scanning text against a predefined list
of offensive terms and masking them with asterisks.

Used to sanitize user input before processing or logging.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import re

from app.constants.values import PROFANITY_LIST
from app.lib.utils.decorators.errors import catch_and_log_errors


@catch_and_log_errors(default_return="[PROFANITY FILTER FAILED]")
def filter_profanity(text: str) -> str:
    """
    Replaces profane words from the input text with asterisks, preserving word shape.

    Words are matched using word boundaries and case-insensitive comparison.

    Args:
        text (str): The input text to sanitize.

    Returns:
        str: The cleaned text with profane words censored.
    """

    def censor(word: str) -> str:
        """
        Censors a word by replacing its inner characters with asterisks.

        Args:
            word (str): A matched profane word.

        Returns:
            str: Censored version, e.g., "damn" -> "d**n"
        """
        return (
            word[0] + "*" * (len(word) - 2) + word[-1]
            if len(word) > 2
            else "*" * len(word)
        )

    # Compile regex to match any word in the profanity list, case-insensitive
    pattern = re.compile(
        r"\b(" + "|".join(PROFANITY_LIST) + r")\b", flags=re.IGNORECASE
    )

    # Replace each matched word with its censored version
    return pattern.sub(lambda m: censor(m.group()), text)
