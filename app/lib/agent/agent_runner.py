"""
agent_runner.py (Class-based)

Runs the main LLM agent pipeline. Accepts user input, constructs context-aware prompts,
queries the model with retry logic, persists the interaction, and optionally performs
automated evaluation of the model's response.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import threading
import uuid
from typing import Any, Generator

from app.config import (
    main_model,
    qa_prompt_version,
    qa_template_name,
    system_template,
    use_eval,
)
from app.db.repositories.session_repository import get_session_repo
from app.enums.errors.agent import AgentErrorType
from app.enums.eval import EvalResultKey, RetrievalDocKey
from app.enums.prompts import JsonKey
from app.lib.agent.agent_utils import (
    build_context,
    persist_conversation,
    render_prompt,
    sanitize_input,
    stream_with_capture,
)
from app.lib.eval.eval_runner import EvaluationRunner
from app.lib.model.model_runner import ModelRunner
from app.lib.tools.registries.tool_registry import TOOL_FUNCTIONS
from app.lib.tools.step_executor import StepExecutor
from app.lib.tools.tool_planner import ToolPlanner
from app.lib.utils.decorators.errors import catch_and_log_errors
from app.lib.utils.decorators.tracing import get_tracer, setup_tracing
from app.lib.utils.logger import setup_logger

# Setup instrumentation
logger = setup_logger()
setup_tracing()
tracer = get_tracer(__name__)


class AgentRunner:
    """
    Orchestrates the core agent pipeline including prompt preparation, model interaction,
    session persistence, and optional evaluation.

    Methods:
        run(user_input, session_id): Executes full pipeline and returns final response.
        stream(user_input, session_id): Streams response without blocking.
    """

    def __init__(self):
        self.eval = EvaluationRunner()
        self.model = ModelRunner()
        self.planner = ToolPlanner(use_llm=False)
        self.step_executor = StepExecutor(TOOL_FUNCTIONS)

    @catch_and_log_errors(
        default_return={
            "error": AgentErrorType.AGENT_RUN,
            JsonKey.RESPONSE_ID: None,
            JsonKey.MESSAGE_ID: None,
            JsonKey.SESSION_ID: None,
        }
    )
    def run(self, user_input: str, session_id: str = None) -> dict[str, Any]:
        """
        Executes the agent pipeline:
        - Sanitizes and builds context
        - Renders a prompt
        - Calls the model
        - Persists the conversation
        - Optionally evaluates in a background thread

        Args:
            user_input (str): The raw user input.
            session_id (str, optional): Session ID for continuity. A new one is created if missing.

        Returns:
            dict: Response metadata including session_id, response_id, message_id, and the model response.
        """
        response_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())

        logger.info(
            "Agent input received",
            input=user_input,
            session_id=session_id,
            message_id=message_id,
        )

        filtered_input = sanitize_input(user_input)
        plan = self.planner.route(filtered_input)
        tool_output = self.step_executor.execute(plan) if plan else None
        context_chunks = build_context(filtered_input)

        if tool_output and isinstance(tool_output, str):
            context_chunks.insert(0, f"Tool result: {tool_output}")

        rendered_prompt = render_prompt(filtered_input, context_chunks)
        logger.debug("Rendered Prompt Preview", preview=rendered_prompt[:200])

        response = self.model.run(rendered_prompt)

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
                    "context_chunks": context_chunks,
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

    def stream(
        self, user_input: str, session_id: str = None
    ) -> Generator[str, None, None]:
        """
        Streams the model response token-by-token for real-time applications.

        Unlike `run()`, this does not block on evaluation and supports an optional
        `on_complete` callback to persist and evaluate the final response.

        Args:
            user_input (str): Raw input from the user.
            session_id (str, optional): Existing session ID. Creates one if not provided.

        Returns:
            Generator[str]: Yields chunks of the model's output.
        """
        response_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())

        logger.info(
            "Agent input received",
            input=user_input,
            session_id=session_id,
            message_id=message_id,
        )

        filtered_input = sanitize_input(user_input)
        plan = self.planner.route(filtered_input)
        tool_output = self.step_executor.execute(plan) if plan else None
        context_chunks = build_context(filtered_input)

        if tool_output and isinstance(tool_output, str):
            context_chunks.insert(0, f"Tool result: {tool_output}")

        rendered_prompt = render_prompt(filtered_input, context_chunks)

        response = self.model.stream(rendered_prompt)

        def _on_stream_complete(final_response: str):

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
                        "context_chunks": context_chunks,
                        JsonKey.RESPONSE_ID: response_id,
                        JsonKey.MESSAGE_ID: message_id,
                        JsonKey.SESSION_ID: session_id,
                        "rendered_prompt": rendered_prompt,
                        "raw_input": user_input,
                    },
                    daemon=True,
                ).start()

        return stream_with_capture(response, on_complete=_on_stream_complete)

    @catch_and_log_errors(
        default_return={"error": AgentErrorType.AGENT_BACKGROUND_EVAL}
    )
    def _background_eval(
        self,
        filtered_input: str,
        response: str,
        context_chunks: list[str],
        response_id: str,
        message_id: str,
        session_id: str,
        rendered_prompt: str,
        raw_input: str,
    ):
        """
        Performs background evaluation in a separate thread.

        Args:
            filtered_input (str): Sanitized user input.
            response (str): The generated model response.
            context_chunks (list[str]): Supporting memory or retrieved documents.
            response_id (str): Unique ID for the response.
            message_id (str): Unique ID for the message.
            session_id (str): Session UUID for the user.
            rendered_prompt (str): Full prompt that was sent to the model.
            raw_input (str): Original user input before sanitization.
        """
        with get_session_repo() as repo:
            conversation_history = repo.get_messages_for_session(session_id)

        eval_result = self.eval.run(
            filtered_input,
            response,
            context_chunks,
            response_id=response_id,
            message_id=message_id,
            session_id=session_id,
            prompt_version=qa_prompt_version,
            template_name=qa_template_name,
            system_prompt=system_template,
            rendered_prompt=rendered_prompt,
            raw_input=raw_input,
            conversation_history=conversation_history,
        )
        if eval_result:
            top_doc = eval_result.get("retrieval", {}).get("docs", [{}])[0]
            logger.info(
                "Evaluation completed",
                rating=eval_result.get(EvalResultKey.RATING),
                helpfulness=eval_result.get(EvalResultKey.HELPFULNESS, "")[:200],
                grounding=eval_result.get(EvalResultKey.GROUNDING),
                hallucination=eval_result.get(EvalResultKey.HALLUCINATION),
                top_chunk=top_doc.get(RetrievalDocKey.CHUNK, "")[:80],
                top_score=top_doc.get(RetrievalDocKey.SCORE),
                top_source=str(top_doc.get(RetrievalDocKey.SOURCE)),
            )
