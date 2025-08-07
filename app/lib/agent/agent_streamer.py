"""
agent_streamer.py

Runs the LLM agent in streaming mode. Streams the response token-by-token,
persisting results and optionally performing background evaluation.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import threading
import uuid
from typing import Generator

from app.config import main_model, output_filters, use_eval
from app.db.repositories.session_repository import get_session_repo
from app.enums.errors.agent import AgentErrorType
from app.enums.eval import EvalResultKey, RetrievalDocKey
from app.enums.prompts import JsonKey
from app.enums.tools import ToolKey
from app.lib.agent.agent_core import AgentCore
from app.lib.agent.agent_utils import persist_conversation, stream_with_capture
from app.lib.eval.eval_core import EvaluationCore
from app.lib.model.model_core import ModelCore
from app.lib.tools.registries.guardrail_registry import GUARDRAIL_FUNCTIONS
from app.lib.utils.decorators.errors import catch_and_log_errors
from app.lib.utils.decorators.tracing import get_tracer, setup_tracing
from app.lib.utils.logger import setup_logger

# Setup instrumentation
logger = setup_logger()
setup_tracing()
tracer = get_tracer(__name__)


class AgentStreamer:
    """
    Orchestrates streaming agent execution.

    Methods:
        stream(user_input, session_id): Streams output token-by-token.
    """

    def __init__(self):
        self.eval = EvaluationCore()
        self.model = ModelCore()
        self.pipeline = AgentCore()

    @catch_and_log_errors(default_return={"error": AgentErrorType.AGENT_STREAM_CAPTURE})
    def stream(
        self, user_input: str, session_id: str = None
    ) -> Generator[str, None, None]:
        response_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())

        filtered_input, rendered_prompt, context_chunks, plan = self.pipeline.build(
            user_input
        )

        response = self.model.stream(rendered_prompt)

        def _on_stream_complete(final_response: str):
            # Apply guardrail filters before persisting or returning
            for filter_name in output_filters:
                filter_func = GUARDRAIL_FUNCTIONS[filter_name][ToolKey.FUNCTION]
                final_response = filter_func(final_response)

            persist_conversation(
                session_id=session_id,
                user_input=user_input,
                response=final_response,
                tokens_used=len(final_response.split()),
                metadata={
                    "model_used": main_model,
                    "tools_enabled": [step["tool"] for step in plan] if plan else [],
                    "eval_enabled": use_eval,
                },
            )

            if use_eval:
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

    def _background_eval(self, **kwargs):
        with get_session_repo() as repo:
            history = repo.get_messages_for_session(kwargs[JsonKey.SESSION_ID])

        result = self.eval.run(
            **kwargs,
            conversation_history=history,
        )

        if result:
            top_doc = result.get("retrieval", {}).get("docs", [{}])[0]
            logger.info(
                "Evaluation completed",
                rating=result.get(EvalResultKey.RATING),
                helpfulness=result.get(EvalResultKey.HELPFULNESS, "")[:200],
                grounding=result.get(EvalResultKey.GROUNDING),
                hallucination=result.get(EvalResultKey.HALLUCINATION),
                top_chunk=top_doc.get(RetrievalDocKey.CHUNK, "")[:80],
                top_score=top_doc.get(RetrievalDocKey.SCORE),
                top_source=str(top_doc.get(RetrievalDocKey.SOURCE)),
            )
