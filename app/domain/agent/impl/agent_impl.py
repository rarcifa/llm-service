"""Module documentation for `app/domain/agent/impl/agent_impl.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

import threading
import uuid
from typing import Generator

from app.common.decorators.errors import error_boundary
from app.common.decorators.tracing import get_tracer, setup_tracing
from app.common.utils.logger import setup_logger
from app.config import config
from app.constants.errors import AGENT_STREAM_CAPTURE
from app.db.repositories.session_repository import get_session_repo
from app.domain.agent.impl.pipeline_impl import PipelineImpl
from app.domain.agent.utils.agent_utils import persist_conversation, stream_with_capture
from app.domain.eval.impl.eval_impl import EvalImpl
from app.domain.provider.impl.provider_impl import ProviderImpl
from app.enums.eval import EvalResultKey, RetrievalDocKey
from app.enums.prompts import JsonKey

logger = setup_logger()
setup_tracing()
tracer = get_tracer(__name__)


class AgentImpl:
    """Summary of `AgentImpl`.

    Attributes:
        eval: Description of `eval`.
        pipeline: Description of `pipeline`.
        provider: Description of `provider`.
    """

    def __init__(self) -> None:
        """Summary of `__init__`.

        Args:
            self: Description of self.

        """
        self.eval = EvalImpl()
        self.provider = ProviderImpl()
        self.pipeline = PipelineImpl()

    @error_boundary(default_return={"error": AGENT_STREAM_CAPTURE})
    def run(
        self, user_input: str, session_id: str | None = None
    ) -> Generator[str, None, None]:
        """Summary of `run`.

        Args:
            self: Description of self.
            user_input (str): Description of user_input.
            session_id (str | None): Description of session_id, default=None.

        Returns:
            Generator[str, None, None]: Description of return value.

        """
        response_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())
        filtered_input, rendered_prompt, context_chunks, plan = self.pipeline.build(
            user_input
        )
        response = self.provider.stream(rendered_prompt)

        def _on_stream_complete(final_response: str) -> None:
            persist_conversation(
                session_id=session_id,
                user_input=user_input,
                response=final_response,
                tokens_used=len(final_response.split()),
                metadata={
                    "model_used": config.models.main.model_id,
                    "tools_enabled": [step["tool"] for step in plan] if plan else [],
                    "eval_enabled": config.eval.enabled,
                },
            )
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
        """Summary of `_background_eval`.

        Args:
            self: Description of self.
            kwargs: Description of kwargs.

        """
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
