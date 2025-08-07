"""
agent_core.py

Shared logic for building prompt context, planning tools, and constructing model input
for both AgentRunner (non-streaming) and AgentStreamer (streaming) classes.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from typing import Tuple

from app.config import memory, retrieval_enabled
from app.enums.tools import ToolKey, ToolName
from app.lib.agent.agent_utils import render_prompt, sanitize_input
from app.lib.tools.registries.tool_registry import TOOL_FUNCTIONS
from app.lib.tools.step_executor import StepExecutor
from app.lib.tools.tool_planner import ToolPlanner


class AgentCore:
    """
    Encapsulates reusable planning and prompt rendering logic.

    This class builds the sanitized input, executes tool planning, retrieves context,
    and prepares the final prompt string for downstream model consumption.
    """

    def __init__(self):
        self.planner = ToolPlanner(use_llm=False)
        self.step_executor = StepExecutor(TOOL_FUNCTIONS)

    def build(self, user_input: str) -> Tuple[str, str, list[str], list[dict]]:
        """
        Prepares the agent pipeline steps:
        - Sanitizes input
        - Plans tool calls
        - Retrieves context (memory + optional retrieval)
        - Renders the final prompt

        Args:
            user_input (str): Raw input from the user

        Returns:
            Tuple[str, str, list[str], list[dict]]:
                - filtered_input (str)
                - rendered_prompt (str)
                - context_chunks (list)
                - plan (list of tool steps)
        """
        filtered_input = sanitize_input(user_input)
        plan = self.planner.route(filtered_input)
        tool_output = self.step_executor.execute(plan) if plan else None

        context_chunks = memory.retrieve_context(filtered_input)

        if tool_output and isinstance(tool_output, str):
            context_chunks.insert(0, f"Tool result: {tool_output}")

        if retrieval_enabled:
            retrieved = TOOL_FUNCTIONS[ToolName.SEARCH_DOCS][ToolKey.FUNCTION](
                filtered_input
            )
            context_chunks += retrieved

        rendered_prompt = render_prompt(filtered_input, context_chunks)

        return filtered_input, rendered_prompt, context_chunks, plan
