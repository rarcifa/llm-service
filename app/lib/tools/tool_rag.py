"""
tool_rag.py

LlamaIndex-powered tool for document Q&A using RAG pipeline.
Compatible with the StepExecutor and ToolPlanner registry system.

Author: Ricardo Arcifa
Created: 2025-08-07
"""

from app.lib.rag.rag_index import query_rag


def ask_docs(input: str) -> str:
    """
    Tool: Ask a question using local knowledge base via RAG.

    Args:
        input (str): User query.

    Returns:
        str: Answer from embedded documents.
    """
    return query_rag(input)
