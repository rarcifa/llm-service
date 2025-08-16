"""Module documentation for `app/domain/tools/utils/calculator.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import ast
import operator as op

from app.common.decorators.errors import error_boundary

_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
}


def eval(node):
    """Summary of `eval`.

    Args:
        node: Description of node.

    Returns:
        Any: Description of return value.

    Raises:
        ValueError: Condition when this is raised.

    """
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("constants other than numbers not allowed")
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](eval(node.left), eval(node.right))
    raise ValueError("unsupported expression")


@error_boundary(default_return="[calculator error]")
def calculator_tool(expression: str) -> str:
    """Summary of `calculator_tool`.

    Args:
        expression (str): Description of expression.

    Returns:
        str: Description of return value.

    """
    expr = (expression or "").strip()
    expr = expr.replace("×", "*").replace("x", "*").replace("X", "*")
    tree = ast.parse(expr, mode="eval")
    val = eval(tree.body)
    return str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
