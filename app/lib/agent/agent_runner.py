"""
agent_runner.py

Runs the LLM agent in blocking (non-streaming) mode. Responsible for building
context-aware prompts, invoking the model, persisting interactions, and triggering eval.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import threading
import uuid
from typing import Any

from app.config import (
    main_model,
    use_eval,
    output_filters
)
from app.enums.errors.agent import AgentErrorType
from app.enums.prompts import JsonKey
from app.enums.eval import EvalResultKey, RetrievalDocKey
from app.enums.tools import ToolKey
from app.lib.agent.agent_utils import persist_conversation
from app.lib.agent.agent_core import AgentCore
from app.lib.eval.eval_core import EvaluationCore
from app.lib.model.model_core import ModelCore
from app.db.repositories.session_repository import get_session_repo
from app.lib.tools.registries.guardrail_registry import GUARDRAIL_FUNCTIONS
from app.lib.utils.decorators.errors import catch_and_log_errors
from app.lib.utils.logger import setup_logger
from app.lib.utils.decorators.tracing import get_tracer, setup_tracing

# Setup instrumentation
logger = setup_logger()
setup_tracing()
tracer = get_tracer(__name__)


class AgentRunner:
    """
    Orchestrates blocking (non-streaming) agent execution.

    Methods:
        run(user_input, session_id): Full run, returns model response and metadata.
    """

    def __init__(self):
        self.eval = EvaluationCore()
        self.model = ModelCore()
        self.pipeline = AgentCore()

    @catch_and_log_errors(
        default_return={
            "error": AgentErrorType.AGENT_RUN,
            JsonKey.RESPONSE_ID: None,
            JsonKey.MESSAGE_ID: None,
            JsonKey.SESSION_ID: None,
        }
    )
    def run(self, user_input: str, session_id: str = None) -> dict[str, Any]:
        response_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())

        filtered_input, rendered_prompt, context_chunks, plan = self.pipeline.build(user_input)

        response = self.model.run(rendered_prompt)
        
        # Apply guardrail filters before persisting or returning
        for filter_name in output_filters:
            filter_func = GUARDRAIL_FUNCTIONS[filter_name][ToolKey.FUNCTION]
            response = filter_func(response)
            
        persist_conversation(
            session_id=session_id,
            user_input=user_input,
            response=response,
            tokens_used=len(response.split()),
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
                    JsonKey.RESPONSE: response,
                    "retrieved_docs": context_chunks,
                    JsonKey.RESPONSE_ID: response_id,
                    JsonKey.MESSAGE_ID: message_id,
                    JsonKey.SESSION_ID: session_id,
                    "rendered_prompt": rendered_prompt,
                    "raw_input": user_input,
                },
                daemon=True,
            ).start()

        return {
            JsonKey.SESSION_ID: session_id,
            JsonKey.RESPONSE_ID: response_id,
            JsonKey.MESSAGE_ID: message_id,
            JsonKey.RESPONSE: response.strip(),
            "prompt": rendered_prompt,
        }

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
