from __future__ import annotations

from .models import (
    IRBinaryOp,
    IRBoolLiteral,
    IRBoolOp,
    IRCompare,
    IRConcat,
    IRExpr,
    IRIfThenElse,
    IRIntLiteral,
    IRLen,
    IRLet,
    IRListLiteral,
    IRSubscript,
    IRUnaryOp,
    IRVar,
)


def render_expr(expr: IRExpr) -> str:
    if isinstance(expr, IRVar):
        return expr.name
    if isinstance(expr, IRIntLiteral):
        return str(expr.value)
    if isinstance(expr, IRBoolLiteral):
        return "True" if expr.value else "False"
    if isinstance(expr, IRListLiteral):
        return "[" + ", ".join(render_expr(item) for item in expr.items) + "]"
    if isinstance(expr, IRUnaryOp):
        if expr.op == "-":
            return f"(-{render_expr(expr.operand)})"
        if expr.op == "not":
            return f"(¬ {render_expr(expr.operand)})"
        raise TypeError(f"Unsupported unary op: {expr.op}")
    if isinstance(expr, IRBinaryOp):
        return f"({render_expr(expr.left)} {expr.op} {render_expr(expr.right)})"
    if isinstance(expr, IRCompare):
        op_map = {
            "==": "=",
            "!=": "≠",
            ">": ">",
            ">=": "≥",
            "<": "<",
            "<=": "≤",
            "in": "∈",
            "not in": "∉",
        }
        op = op_map.get(expr.op, expr.op)
        return f"({render_expr(expr.left)} {op} {render_expr(expr.right)})"
    if isinstance(expr, IRBoolOp):
        connective = "∧" if expr.op == "and" else "∨"
        return f"({render_expr(expr.left)} {connective} {render_expr(expr.right)})"
    if isinstance(expr, IRIfThenElse):
        return (
            f"(if {render_expr(expr.condition)} then "
            f"{render_expr(expr.then_expr)} else {render_expr(expr.else_expr)})"
        )
    if isinstance(expr, IRLet):
        return f"(let {expr.name} := {render_expr(expr.value)}; {render_expr(expr.body)})"
    if isinstance(expr, IRSubscript):
        return f"({render_expr(expr.collection)}.get! (Int.toNat {render_expr(expr.index)}))"
    if isinstance(expr, IRLen):
        return f"(Int.ofNat ({render_expr(expr.collection)}.length))"
    if isinstance(expr, IRConcat):
        return f"({render_expr(expr.left)} ++ {render_expr(expr.right)})"
    raise TypeError(f"Unsupported IR expression type: {type(expr).__name__}")
