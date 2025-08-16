"""Module documentation for `app/domain/ingestion/utils/ingestion_utils.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from app.common.decorators.errors import error_boundary
from app.constants.errors import CHUNK_TEXT, SAFE_METADATA


@error_boundary(default_return={"error": CHUNK_TEXT})
def chunk_text(text: str, size: int) -> list[str]:
    """Summary of `chunk_text`.

    Args:
        text (str): Description of text.
        size (int): Description of size.

    Returns:
        list[str]: Description of return value.

    """
    return [text[i : i + size] for i in range(0, len(text), size)]


@error_boundary(default_return={"error": SAFE_METADATA})
def safe_metadata(meta: dict, *, max_len: int = 8192) -> dict:
    """Summary of `safe_metadata`.

    Args:
        meta (dict): Description of meta.
        max_len (int): Description of max_len, default=8192.

    Returns:
        dict: Description of return value.

    """
    out = {}
    for k, v in (meta or {}).items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            out[k] = v
        else:
            s = str(v)
            out[k] = s if len(s) <= max_len else s[:max_len]
    return out
