import hashlib


def sha256(text: str) -> str:
    """Summary of `sha256`.

    Args:
        text (str): Description of text.

    Returns:
        str: Description of return value.

    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()