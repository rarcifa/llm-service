from app.common.decorators.errors import catch_and_log_errors
import ast, operator as op

_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.USub: op.neg, ast.Mod: op.mod, ast.FloorDiv: op.floordiv,
}

def _eval(node):
    if isinstance(node, ast.Num): return node.n
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)): return node.value
        raise ValueError("constants other than numbers not allowed")
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    raise ValueError("unsupported expression")

@catch_and_log_errors(default_return="[calculator error]")
def calculator_tool(expression: str) -> str:
    # normalize and strip
    expr = (expression or "").strip()
    expr = expr.replace("×", "*").replace("x", "*").replace("X", "*")
    tree = ast.parse(expr, mode="eval")
    val = _eval(tree.body)
    return str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
