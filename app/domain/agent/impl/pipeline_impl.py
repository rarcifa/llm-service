"""Module documentation for `app/domain/agent/impl/pipeline.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.config import config
from app.domain.agent.base.agent_base import AgentBase
from app.domain.agent.utils.agent_utils import render_prompt, sanitize_io
from app.domain.memory.impl.memory_impl import MemoryImpl
from app.domain.tools.impl.planner_impl import PlannerImpl
from app.domain.tools.impl.step_executor import StepExecutorImpl


class PipelineImpl(AgentBase):
    """Summary of `PipelineImpl`.

    Attributes:
        memory: Description of `memory`.
        planner: Description of `planner`.
        step_executor: Description of `step_executor`.
    """

    def __init__(self) -> None:
        """Summary of `__init__`.

        Args:
            self: Description of self.

        """
        self.planner = PlannerImpl(use_llm=True)
        self.step_executor = StepExecutorImpl()
        self.memory = MemoryImpl(window_size=config.memory.window_size)

    def build(
        self, user_input: str
    ) -> Tuple[str, str, List[str], List[Dict[str, Any]]]:
        """Summary of `build`.

        Args:
            self: Description of self.
            user_input (str): Description of user_input.

        Returns:
            Tuple[str, str, List[str], List[Dict[str, Any]]]: Description of return value.

        """
        filtered_input = sanitize_io(user_input)
        plan: List[Dict[str, Any]] = self.planner.route(filtered_input)
        tool_output = self.step_executor.execute(plan) if plan else None
        context_chunks = self.memory.retrieve_context(filtered_input)
        if tool_output and isinstance(tool_output, str) and tool_output.strip():
            context_chunks.insert(0, tool_output.strip())
        rendered_prompt = render_prompt(filtered_input, context_chunks)
        return (filtered_input, rendered_prompt, context_chunks, plan)
