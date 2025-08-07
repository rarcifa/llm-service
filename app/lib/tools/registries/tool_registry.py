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

from app.lib.tools.tool_rag import ask_docs
from app.lib.tools.vector_search import retrieve_relevant_docs

TOOL_FUNCTIONS: Dict[str, Dict[str, Callable | str]] = {
    "search_docs": {
        "function": retrieve_relevant_docs,
        "description": "Retrieves relevant documents or context from the vector store.",
    },
    "summarize": {
        "function": lambda input: f"[summarize called with: {input}]",
        "description": "Summarizes a long passage into a short summary.",
    },
    "calculator": {
        "function": lambda input: f"[calculator called with: {input}]",
        "description": "Performs basic arithmetic or evaluation of math expressions.",
    },
    "ask_docs": {
        "function": ask_docs,
        "description": "Ask the embedded document index via LlamaIndex RAG pipeline.",
    },
}
