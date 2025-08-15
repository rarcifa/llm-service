"""Module documentation for `app/domain/ingestion/utils/text.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""


def chunk_text(text: str, size: int) -> list[str]:
    """Summary of `chunk_text`.

    Args:
        text (str): Description of text.
        size (int): Description of size.

    Returns:
        list[str]: Description of return value.

    """
    return [text[i : i + size] for i in range(0, len(text), size)]
