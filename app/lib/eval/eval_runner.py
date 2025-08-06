"""
eval_service.py

Defines the EvaluationService class to encapsulate the logic for evaluating
LLM-generated responses. Computes quality scores (helpfulness, grounding,
hallucination), builds evaluation metadata, and emits trace logs.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import datetime
import uuid
from typing import Any

from app.enums.eval import EvalKey, TraceMetaKey
from app.lib.eval.eval_utils import compute_scores, trace_eval_span
from app.lib.utils.decorators.tracing import trace_span
from app.lib.utils.logger import setup_logger

logger = setup_logger()


class EvaluationRunner:
    """
    Service responsible for evaluating agent responses.

    Methods:
        run(...): Evaluates a response and emits span metadata.
    """

    @trace_span(EvalKey.AGENT)
    def run(
        self,
        filtered_input: str,
        response: str,
        retrieved_docs: list[str],
        response_id: str,
        message_id: str,
        session_id: str,
        prompt_version: str = None,
        template_name: str = None,
        system_prompt: str = None,
        rendered_prompt: str = None,
        raw_input: str = None,
        conversation_history: list[str] = None,
    ) -> dict[str, Any]:
        """
        Evaluates an agent's response using internal evaluation tools
        and emits trace metadata.

        Args:
            filtered_input (str): Cleaned user input.
            response (str): Model-generated response.
            retrieved_docs (list[str]): Supporting docs or memory.
            response_id (str): UUID of the response.
            message_id (str): UUID of the message.
            session_id (str): UUID of the session.
            prompt_version (str, optional): Version of the prompt.
            template_name (str, optional): Prompt template name.
            system_prompt (str, optional): System prompt text.
            rendered_prompt (str, optional): Final rendered prompt.
            raw_input (str, optional): Original user input.
            conversation_history (list[str], optional): Prior chat turns.

        Returns:
            dict[str, Any]: Evaluation scores and optional retrieval metadata.
        """
        trace_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()

        scores = compute_scores(
            filtered_input, response, retrieved_docs, conversation_history
        )

        meta = {
            TraceMetaKey.TRACE_ID: trace_id,
            TraceMetaKey.TRACE_TIMESTAMP: timestamp,
            TraceMetaKey.RESPONSE_ID: response_id,
            TraceMetaKey.MESSAGE_ID: message_id,
            TraceMetaKey.SESSION_ID: session_id,
            TraceMetaKey.PROMPT_VERSION: prompt_version or "unknown",
            TraceMetaKey.PROMPT_TEMPLATE_NAME: template_name or "default",
            TraceMetaKey.PROMPT_SYSTEM_PROMPT: system_prompt or "",
            TraceMetaKey.PROMPT_RENDERED_PREVIEW: rendered_prompt or "",
            TraceMetaKey.PROMPT_RENDERED_TOKENS: (
                len(rendered_prompt.split()) if rendered_prompt else 0
            ),
            TraceMetaKey.PROMPT_TEMPLATE_TOKENS: (
                len(system_prompt.split()) if system_prompt else 0
            ),
            TraceMetaKey.INPUT_RAW: raw_input or filtered_input,
            TraceMetaKey.INPUT_FILTERED: filtered_input,
            TraceMetaKey.INPUT_LENGTH: len(raw_input or filtered_input),
            TraceMetaKey.OUTPUT_RESPONSE: response,
            TraceMetaKey.OUTPUT_RESPONSE_LENGTH: len(response),
        }

        retrieval = scores.pop("retrieval", {})
        retrieval_trace_attrs = {}

        if "docs" in retrieval:
            retrieval_trace_attrs[TraceMetaKey.RETRIEVAL_DOCS_COUNT] = len(
                retrieval["docs"]
            )
            if retrieval["docs"]:
                top_doc = retrieval["docs"][0]
                retrieval_trace_attrs[TraceMetaKey.RETRIEVAL_TOP_CHUNK] = top_doc[
                    "chunk"
                ][:100]
                retrieval_trace_attrs[TraceMetaKey.RETRIEVAL_TOP_SCORE] = top_doc[
                    "score"
                ]
                retrieval_trace_attrs[TraceMetaKey.RETRIEVAL_TOP_SOURCE] = top_doc[
                    "source"
                ]

        trace_eval_span(meta, {**scores, **retrieval_trace_attrs})

        return {**scores, "retrieval": retrieval}
