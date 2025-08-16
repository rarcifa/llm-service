"""Module documentation for `app/domain/provider/utils/provider_utils.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from __future__ import annotations

from typing import List

from jinja2 import Environment, meta

from app.common.decorators.errors import error_boundary


@error_boundary(default_return=["__template_error__"])
def verify_prompt_variables(template_str: str, provided_vars: dict) -> List[str]:
    """Summary of `verify_prompt_variables`.

    Args:
        template_str (str): Description of template_str.
        provided_vars (dict): Description of provided_vars.

    Returns:
        List[str]: Description of return value.

    """
    env = Environment()
    parsed = env.parse(template_str)
    required = meta.find_undeclared_variables(parsed)
    return [var for var in required if var not in provided_vars]
