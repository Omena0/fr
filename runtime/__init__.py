"""
FrScript C Runtime VM

This package contains the C-based virtual machine runtime for FrScript.
"""

# Minimal eval_expr for parse-time constant folding
import ast
import operator as _operator

_BINOPS = {
    ast.Add: _operator.add,
    ast.Sub: _operator.sub,
    ast.Mult: _operator.mul,
    ast.Div: _operator.truediv,
    ast.FloorDiv: _operator.floordiv,
    ast.Mod: _operator.mod,
    ast.Pow: _operator.pow,
}

_UNITOPS = {
    ast.UAdd: _operator.pos,
    ast.USub: _operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _BINOPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        return _UNITOPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Cannot eval expression node: {type(node)}")


def eval_expr(expr_str):
    """Evaluate a simple arithmetic expression string at parse time.

    Returns the numeric result, or None if the expression cannot be evaluated.
    """
    try:
        tree = ast.parse(expr_str, mode="eval")
        return _eval_node(tree.body)
    except Exception:
        return None


# Flag used by parser for parse-time evaluation mode
runtime = True
