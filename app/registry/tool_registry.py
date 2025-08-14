"""
tool_registry.py

Defines a central registry of available tools that can be invoked dynamically by name.
Each tool entry includes:
- A callable function reference
- A human-readable description of what the tool does

This registry supports systems that dispatch tools (e.g., via tool names in prompts or config).

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from typing import Callable, Dict

from app.domain.retrieval.impl.rag_retriever_impl import RagRetrieverImpl
from app.domain.tools.utils.calculator import calculator_tool

retriever = RagRetrieverImpl()

TOOL_FUNCTIONS: Dict[str, Dict[str, Callable | str]] = {
    "search_docs": {
        "function": retriever.retrieve,
        "description": "Retrieves relevant documents or context from the vector store.",
    },
    "summarize": {
        "function": lambda input: f"[summarize called with: {input}]",
        "description": "Summarizes a long passage into a short summary.",
    },
    "calculator": {
        "function": calculator_tool,
        "description": "Performs basic arithmetic or evaluation of math expressions.",
    },
    "ask_docs": {
        "function": retriever.query,
        "description": "Ask the embedded document index via LlamaIndex RAG pipeline.",
    },
}
