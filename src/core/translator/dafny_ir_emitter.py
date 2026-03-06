from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from ..ir import VerificationCondition
from ..ir.models import (
    IRBinaryOp,
    IRBoolLiteral,
    IRBoolOp,
    IRCompare,
    IRConcat,
    IRExpr,
    IRFunction,
    IRIfThenElse,
    IRIntLiteral,
    IRLen,
    IRLet,
    IRListLiteral,
    IRProgram,
    IRSubscript,
    IRType,
    IRUnaryOp,
    IRVar,
)


class DafnyIREmitter:
    def emit(self, program: IRProgram, conditions: List[VerificationCondition]) -> str:
        vc_by_fn: Dict[str, List[VerificationCondition]] = defaultdict(list)
        for item in conditions:
            vc_by_fn[item.function.name].append(item)

        methods: List[str] = []
        for fn in program.functions:
            methods.append(self._emit_method(fn, vc_by_fn.get(fn.name, [])))
        return "\n\n".join(methods)

    def _emit_method(self, fn: IRFunction, conditions: List[VerificationCondition]) -> str:
        params = ", ".join(f"{item.name}: {self._type_to_dafny(item.type)}" for item in fn.params)
        lines = [
            f"method {fn.name}({params}) returns (result: {self._type_to_dafny(fn.return_type)})",
        ]
        for vc in conditions:
            lines.append(f"  ensures {self._lean_goal_to_dafny(vc.proposition)}")
            lines.append(f"  // OBLIGATION: {vc.obligation.property}")
        lines.append("{")
        lines.extend(f"  {line}" for line in self._emit_body(fn.body))
        lines.append("}")
        return "\n".join(lines)

    def _emit_body(self, expr: IRExpr) -> List[str]:
        if isinstance(expr, IRLet):
            return [f"var {expr.name} := {self._render_expr(expr.value)};"] + self._emit_body(expr.body)
        return [f"result := {self._render_expr(expr)};"]

    def _render_expr(self, expr: IRExpr) -> str:
        if isinstance(expr, IRVar):
            return expr.name
        if isinstance(expr, IRIntLiteral):
            return str(expr.value)
        if isinstance(expr, IRBoolLiteral):
            return "true" if expr.value else "false"
        if isinstance(expr, IRListLiteral):
            return "[" + ", ".join(self._render_expr(item) for item in expr.items) + "]"
        if isinstance(expr, IRUnaryOp):
            if expr.op == "-":
                return f"(-{self._render_expr(expr.operand)})"
            if expr.op == "not":
                return f"(!{self._render_expr(expr.operand)})"
        if isinstance(expr, IRBinaryOp):
            return f"({self._render_expr(expr.left)} {expr.op} {self._render_expr(expr.right)})"
        if isinstance(expr, IRCompare):
            op = {
                "==": "==",
                "!=": "!=",
                ">": ">",
                ">=": ">=",
                "<": "<",
                "<=": "<=",
                "in": "in",
                "not in": "!in",
            }.get(expr.op, expr.op)
            return f"({self._render_expr(expr.left)} {op} {self._render_expr(expr.right)})"
        if isinstance(expr, IRBoolOp):
            connective = "&&" if expr.op == "and" else "||"
            return f"({self._render_expr(expr.left)} {connective} {self._render_expr(expr.right)})"
        if isinstance(expr, IRIfThenElse):
            return (
                f"(if {self._render_expr(expr.condition)} then "
                f"{self._render_expr(expr.then_expr)} else {self._render_expr(expr.else_expr)})"
            )
        if isinstance(expr, IRSubscript):
            return f"{self._render_expr(expr.collection)}[{self._render_expr(expr.index)}]"
        if isinstance(expr, IRLen):
            return f"|{self._render_expr(expr.collection)}|"
        if isinstance(expr, IRConcat):
            return f"({self._render_expr(expr.left)} + {self._render_expr(expr.right)})"
        if isinstance(expr, IRLet):
            return self._render_expr(expr.body)
        raise TypeError(f"Unsupported IR expression for Dafny: {type(expr).__name__}")

    def _lean_goal_to_dafny(self, proposition: str) -> str:
        return (
            proposition.replace("∧", "&&")
            .replace("∨", "||")
            .replace("¬", "!")
            .replace("≥", ">=")
            .replace("≤", "<=")
            .replace("≠", "!=")
            .replace("→", "==>")
            .replace("Int.ofNat", "")
        )

    def _type_to_dafny(self, ir_type: IRType) -> str:
        if ir_type == IRType.INT:
            return "int"
        if ir_type == IRType.BOOL:
            return "bool"
        if ir_type == IRType.LIST_INT:
            return "seq<int>"
        return "int"
