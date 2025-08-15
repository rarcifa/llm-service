"""Streaming agent implementation.

Runs the LLM agent in streaming mode, returning tokens incrementally while
persisting results and (optionally) launching background evaluation.

Author: Ricardo Arcifa
Created: 2025-02-03
"""
from __future__ import annotations


import re
import threading
import uuid
from typing import Generator

from app.common.decorators.errors import catch_and_log_errors
from app.common.decorators.tracing import get_tracer, setup_tracing
from app.common.utils.logger import setup_logger
from app.config import config
from app.db.repositories.session_repository import get_session_repo
from app.domain.agent.impl.persistence import persist_conversation
from app.domain.agent.impl.pipeline import Pipeline
from app.domain.agent.utils.agent_utils import sanitize_io, stream_with_capture
from app.domain.eval.impl.eval_impl import EvalImpl
from app.domain.provider.impl.ollama_provider import Provider
from app.enums.errors.agent import AgentErrorType
from app.enums.eval import EvalResultKey, RetrievalDocKey
from app.enums.prompts import JsonKey
from app.enums.tools import ToolKey

# Setup instrumentation
logger = setup_logger()
setup_tracing()
tracer = get_tracer(__name__)

class AgentImpl:
    """Orchestrates streaming agent execution."""

    def __init__(self) -> None:
        """Initialize evaluation, provider, and pipeline."""
        self.eval = EvalImpl()
        self.provider = Provider()
        self.pipeline = Pipeline()

    @catch_and_log_errors(default_return={"error": AgentErrorType.AGENT_STREAM_CAPTURE})
    def run(
        self, user_input: str, session_id: str | None = None
    ) -> Generator[str, None, None]:
        """Stream a model response while capturing full output."""
        response_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())

        filtered_input, rendered_prompt, context_chunks, plan = self.pipeline.build(
            user_input
        )
        response = self.provider.stream(rendered_prompt)

        def _on_stream_complete(final_response: str) -> None:

            # 2) Persist conversation
            persist_conversation(
                session_id=session_id,
                user_input=user_input,
                response=final_response,
                tokens_used=len(final_response.split()),
                metadata={
                    "model_used": config.models.main.model_id,  # ensure string id
                    "tools_enabled": [step["tool"] for step in plan] if plan else [],
                    "eval_enabled": config.eval.enabled,
                },
            )

            # 3) Optional background evaluation
            if config.eval.enabled:
                threading.Thread(
                    target=self._background_eval,
                    kwargs={
                        "filtered_input": filtered_input,
                        JsonKey.RESPONSE: final_response,
                        "retrieved_docs": context_chunks,
                        JsonKey.RESPONSE_ID: response_id,
                        JsonKey.MESSAGE_ID: message_id,
                        JsonKey.SESSION_ID: session_id,
                        "rendered_prompt": rendered_prompt,
                        "raw_input": user_input,
                    },
                    daemon=True,
                ).start()

        return stream_with_capture(response, on_complete=_on_stream_complete)

    def _background_eval(self, **kwargs) -> None:
        """Run evaluation asynchronously after response completion."""
        with get_session_repo() as repo:
            history = repo.get_messages_for_session(kwargs[JsonKey.SESSION_ID])

        result = self.eval.run(**kwargs, conversation_history=history)

        if result:
            docs = result.get("retrieval", {}).get("docs") or []
            top_doc = docs[0] if docs else {}
            logger.info(
                "Evaluation completed",
                rating=result.get(EvalResultKey.RATING),
                helpfulness=(result.get(EvalResultKey.HELPFULNESS, "") or "")[:200],
                grounding=result.get(EvalResultKey.GROUNDING),
                hallucination=result.get(EvalResultKey.HALLUCINATION),
                top_chunk=(top_doc.get(RetrievalDocKey.CHUNK, "") or "")[:80],
                top_score=top_doc.get(RetrievalDocKey.SCORE),
                top_source=str(top_doc.get(RetrievalDocKey.SOURCE)),
            )