"""Provider utilities (pure functions only).

Author: Ricardo Arcifa
Created: 2025-02-03
"""

from __future__ import annotations

from typing import List

from jinja2 import Environment, meta
from app.common.decorators.errors import catch_and_log_errors


@catch_and_log_errors(default_return=["__template_error__"])
def verify_prompt_variables(template_str: str, provided_vars: dict) -> List[str]:
    """Return missing Jinja2 template variables."""
    env = Environment()
    parsed = env.parse(template_str)
    required = meta.find_undeclared_variables(parsed)
    return [var for var in required if var not in provided_vars]
