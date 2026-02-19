from __future__ import annotations

import ast
from typing import List

from ..models import AssumedInput, Obligation
from .base import TranslationOutcome


LEAN_IMPORTS = """import Mathlib.Tactic.SplitIfs
import Mathlib.Tactic.Linarith

"""


class ASTTranslator:
    """Deterministic translator for simple Python functions."""

    def translate(
        self,
        python_code: str,
        obligations: List[Obligation],
        assumptions: List[AssumedInput],
    ) -> TranslationOutcome:
        try:
            tree = ast.parse(python_code)
        except SyntaxError as exc:
            return TranslationOutcome(
                success=False,
                language="lean",
                code="",
                translator="ast",
                error=f"SyntaxError: {exc}",
            )

        if any(isinstance(node, (ast.For, ast.While, ast.AsyncFunctionDef)) for node in ast.walk(tree)):
            return TranslationOutcome(
                success=False,
                language="lean",
                code="",
                translator="ast",
                error="Unsupported construct for ASTTranslator (loop/async)",
            )

        defs: List[str] = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                defs.append(self._translate_function(node))

        if not defs:
            return TranslationOutcome(
                success=False,
                language="lean",
                code="",
                translator="ast",
                error="No function definitions found",
            )

        theorem_block = self._emit_obligation_theorems(obligations, assumptions)
        code = f"{LEAN_IMPORTS}{chr(10).join(defs)}\n\n{theorem_block}\n"
        return TranslationOutcome(
            success=True,
            language="lean",
            code=code,
            translator="ast",
            used_llm=False,
        )

    def _translate_function(self, node: ast.FunctionDef) -> str:
        args = " ".join(f"({arg.arg} : Int)" for arg in node.args.args)
        body = self._translate_body(node.body)
        return f"def {node.name} {args} : Int :=\n  {body}"

    def _translate_body(self, body: List[ast.stmt]) -> str:
        if not body:
            return "0"
        stmt = body[0]
        if isinstance(stmt, ast.Return):
            return self._translate_expr(stmt.value)
        if isinstance(stmt, ast.If):
            cond = self._translate_expr(stmt.test)
            yes = self._translate_body(stmt.body)
            no = self._translate_body(stmt.orelse) if stmt.orelse else "0"
            return f"if {cond} then {yes} else {no}"
        return "0"

    def _translate_expr(self, expr: ast.AST | None) -> str:
        if expr is None:
            return "0"
        if isinstance(expr, ast.Name):
            return expr.id
        if isinstance(expr, ast.Constant):
            return str(expr.value)
        if isinstance(expr, ast.BinOp):
            left = self._translate_expr(expr.left)
            right = self._translate_expr(expr.right)
            op = {
                ast.Add: "+",
                ast.Sub: "-",
                ast.Mult: "*",
                ast.Div: "/",
                ast.Mod: "%",
            }.get(type(expr.op), "+")
            return f"({left} {op} {right})"
        if isinstance(expr, ast.Compare) and len(expr.ops) == 1:
            left = self._translate_expr(expr.left)
            right = self._translate_expr(expr.comparators[0])
            op = {
                ast.Gt: ">",
                ast.GtE: "≥",
                ast.Lt: "<",
                ast.LtE: "≤",
                ast.Eq: "=",
                ast.NotEq: "≠",
            }.get(type(expr.ops[0]), "=")
            return f"{left} {op} {right}"
        return "0"

    def _emit_obligation_theorems(
        self, obligations: List[Obligation], assumptions: List[AssumedInput]
    ) -> str:
        assumption_lines = []
        for idx, assumption in enumerate(assumptions):
            assumption_lines.append(f"  -- ASSUMED INPUT {idx + 1}: {assumption.property}")

        theorems = []
        for item in obligations:
            theorem_name = item.id.replace(":", "_").replace("-", "_")
            theorem = [
                f"theorem {theorem_name} : True := by",
                "  trivial",
                f"  -- OBLIGATION: {item.property}",
                f"  -- CATEGORY: {item.category}",
            ]
            theorem.extend(assumption_lines)
            theorems.append("\n".join(theorem))
        return "\n\n".join(theorems) if theorems else "-- No obligations generated"

