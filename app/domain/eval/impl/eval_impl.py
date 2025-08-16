"""Module documentation for `app/domain/eval/impl/eval_impl.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

import datetime
import uuid
from typing import Any

from app.common.decorators.tracing import get_tracer, setup_tracing, trace_span
from app.common.utils.logger import setup_logger
from app.config import config
from app.domain.eval.base.eval_base import EvalBase
from app.domain.eval.utils.eval_utils import compute_scores, trace_eval_span
from app.enums.eval import EvalKey, TraceMetaKey

logger = setup_logger()
setup_tracing()
tracer = get_tracer(__name__)


class EvalImpl(EvalBase):
    """Summary of `EvalImpl`."""

    @trace_span(EvalKey.AGENT)
    def run(
        self,
        *,
        filtered_input: str,
        response: str,
        retrieved_docs: list[str],
        response_id: str,
        message_id: str,
        session_id: str,
        prompt_version: str | None = None,
        template_name: str | None = None,
        system_prompt: str | None = None,
        rendered_prompt: str | None = None,
        raw_input: str | None = None,
        conversation_history: list[str] | None = None,
    ) -> dict[str, Any]:
        """Summary of `run`.

        Args:
            self: Description of self.
            filtered_input (str): Description of filtered_input.
            response (str): Description of response.
            retrieved_docs (list[str]): Description of retrieved_docs.
            response_id (str): Description of response_id.
            message_id (str): Description of message_id.
            session_id (str): Description of session_id.
            prompt_version (str | None): Description of prompt_version, default=None.
            template_name (str | None): Description of template_name, default=None.
            system_prompt (str | None): Description of system_prompt, default=None.
            rendered_prompt (str | None): Description of rendered_prompt, default=None.
            raw_input (str | None): Description of raw_input, default=None.
            conversation_history (list[str] | None): Description of conversation_history, default=None.

        Returns:
            dict[str, Any]: Description of return value.

        """
        trace_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        scores = compute_scores(
            filtered_input=filtered_input,
            response=response,
            retrieved_docs=retrieved_docs,
            conversation_history=conversation_history,
            helpfulness_template=config.prompts.eval.helpfulness.template,
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
                retrieval_trace_attrs[TraceMetaKey.RETRIEVAL_TOP_CHUNK] = top_doc.get(
                    "chunk", ""
                )[:100]
                retrieval_trace_attrs[TraceMetaKey.RETRIEVAL_TOP_SCORE] = top_doc.get(
                    "score"
                )
                retrieval_trace_attrs[TraceMetaKey.RETRIEVAL_TOP_SOURCE] = top_doc.get(
                    "source"
                )
        trace_eval_span(meta, {**scores, **retrieval_trace_attrs})
        return {**scores, "retrieval": retrieval}
