"""
hallucination_filter.py

Implements simple pattern-based filtering of hallucinations.
This module scans user input for suspicious patterns commonly used to manipulate LLM behavior.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from app.lib.eval.eval_utils import detect_hallucination


def filter_hallucinations(response: str) -> str:
    """
    Flags or transforms the response based on hallucination level.

    For now, this is a stub. In future, it could redact or rewrite risky output.

    Args:
        response (str): The raw model response.

    Returns:
        str: The (possibly modified) response.
    """
    # You may want to actually *modify* the response here if HIGH
    risk = detect_hallucination(response, [])
    
    if risk == "HIGH":
        return "[Warning: Potential hallucination detected]\n\n" + response
    return response