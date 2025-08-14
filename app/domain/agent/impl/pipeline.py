"""Concrete agent pipeline implementation.

Composes sanitize → plan → (optional) tool exec → memory context → render prompt.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.config import CFG
from app.domain.agent.base.agent_base import AgentBase
from app.domain.agent.utils.agent_utils import render_prompt, sanitize_input
from app.domain.memory.impl.pgvector_memory import MemoryImpl
from app.domain.tools.impl.step_executor import StepExecutorImpl
from app.domain.tools.impl.tool_planner import ToolPlanner
from app.registry.tool_registry import TOOL_FUNCTIONS


class Pipeline(AgentBase):
    """Concrete pipeline that wires planner, executor, memory, and renderer."""

    def __init__(self) -> None:
        self.planner = ToolPlanner(use_llm=True)
        self.step_executor = StepExecutorImpl(TOOL_FUNCTIONS)
        # pgvector-backed memory (no external repo DI needed)
        self.memory = MemoryImpl(window_size=CFG.memory.window_size)

    def build(
        self, user_input: str
    ) -> Tuple[str, str, List[str], List[Dict[str, Any]]]:
        filtered_input = sanitize_input(user_input)
        plan: List[Dict[str, Any]] = self.planner.route(filtered_input)

        tool_output = self.step_executor.execute(plan) if plan else None
        context_chunks = self.memory.retrieve_context(filtered_input)

        if tool_output and isinstance(tool_output, str) and tool_output.strip():
            context_chunks.insert(0, tool_output.strip())

        rendered_prompt = render_prompt(filtered_input, context_chunks)
        return filtered_input, rendered_prompt, context_chunks, plan
