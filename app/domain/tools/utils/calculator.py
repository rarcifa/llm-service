from __future__ import annotations
import ast
import operator as op
from app.common.decorators.errors import catch_and_log_errors

# Allowed operations
_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.USub: op.neg, ast.Mod: op.mod, ast.FloorDiv: op.floordiv,
}

def _eval(node):
    if isinstance(node, ast.Num):      # literal number (py<3.8)
        return node.n
    if isinstance(node, ast.Constant): # literal number (py>=3.8)
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("constants other than numbers not allowed")
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    raise ValueError("unsupported expression")

@catch_and_log_errors(default_return="[calculator error]")
def calculator_tool(expr: str) -> str:
    # normalize “x” to “*” and strip whitespace
    expr = (expr or "").strip().replace(" x ", " * ").replace(" X ", " * ")
    tree = ast.parse(expr, mode="eval")
    val = _eval(tree.body)
    # clean float formatting (2.0 -> 2)
    return str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
