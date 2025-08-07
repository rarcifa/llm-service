"""
rag_index.py - Llam aIndex-based RAG helper.

Author: Ricardo Arcifa
Created: 2025-08-07
"""

from pathlib import Path
from typing import Optional

from llama_index.core import ServiceContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.config import (
    chroma_path,
    main_max_tokens,
    main_model,
    main_temperature,
    rag_model,
)

_index: Optional[VectorStoreIndex] = None


def _get_context() -> ServiceContext:
    return ServiceContext.from_defaults(
        llm=LlamaCPP(
            model_path=main_model,
            temperature=main_temperature,
            context_window=main_max_tokens,
        ),
        embed_model=HuggingFaceEmbedding(model_name=rag_model),
    )


def _get_vector_index() -> VectorStoreIndex:
    global _index
    if _index is None:
        vector_store = ChromaVectorStore(persist_dir=Path(chroma_path))
        _index = VectorStoreIndex.from_vector_store(
            vector_store,
            service_context=_get_context(),
        )
    return _index


def query_rag(question: str) -> str:
    engine = _get_vector_index().as_query_engine(
        similarity_top_k=4,
        response_mode="compact",
    )
    return str(engine.query(question))
