from __future__ import annotations

import re
from typing import List

from ..ir import VerificationCondition, render_expr
from ..ir.models import IRFunction, IRProgram
from ..models import AssumedInput


LEAN_IMPORTS = """import Mathlib.Tactic.SplitIfs
import Mathlib.Tactic.Linarith

"""


class LeanIREmitter:
    def emit(
        self,
        program: IRProgram,
        conditions: List[VerificationCondition],
        assumptions: List[AssumedInput],
    ) -> str:
        defs = [self._emit_function(fn) for fn in program.functions]
        theorems = [self._emit_theorem(vc, assumptions) for vc in conditions]
        return f"{LEAN_IMPORTS}{chr(10).join(defs)}\n\n{chr(10).join(theorems)}\n"

    def _emit_function(self, fn: IRFunction) -> str:
        params = " ".join(f"({param.name} : {param.type.value})" for param in fn.params)
        body = render_expr(fn.body)
        return f"def {fn.name} {params} : {fn.return_type.value} :=\n  {body}"

    def _emit_theorem(self, vc: VerificationCondition, assumptions: List[AssumedInput]) -> str:
        params = " ".join(
            f"({param.name} : {param.type.value})" for param in vc.function.params
        )
        hyps = self._emit_assumption_hypotheses(assumptions)
        header = f"theorem {vc.theorem_name} {params}{hyps} : {vc.proposition} := by"
        proof_lines = self._proof_lines(vc)
        comment_lines = [
            f"  -- OBLIGATION: {vc.obligation.property}",
            f"  -- CATEGORY: {vc.obligation.category}",
        ]
        for idx, assumption in enumerate(assumptions):
            comment_lines.append(f"  -- ASSUMED INPUT {idx + 1}: {assumption.property}")
        return "\n".join([header, *proof_lines, *comment_lines]) + "\n"

    def _emit_assumption_hypotheses(self, assumptions: List[AssumedInput]) -> str:
        parts: List[str] = []
        for idx, assumption in enumerate(assumptions):
            parsed = _parse_assumption_to_lean(assumption.property)
            if parsed:
                parts.append(f" (h_assump_{idx + 1} : {parsed})")
        return "".join(parts)

    def _proof_lines(self, vc: VerificationCondition) -> List[str]:
        fn_name = vc.function.name
        if vc.proof_kind == "non_negativity":
            return [
                f"  unfold {fn_name}",
                "  try split_ifs at *",
                "  simp_all",
                "  try linarith",
                "  try omega",
            ]
        if vc.proof_kind == "bounds":
            return [
                f"  unfold {fn_name}",
                "  try split_ifs at *",
                "  simp_all",
                "  try linarith",
                "  try omega",
            ]
        if vc.proof_kind == "uniqueness":
            return [
                f"  unfold {fn_name}",
                "  try split_ifs at *",
                "  simp_all",
            ]
        return [
            "  -- Unsupported proof kind emitted conservatively.",
            "  aesop",
        ]


_ASSUMPTION_BINARY_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(>=|<=|>|<|==|!=)\s*(-?[A-Za-z_0-9]+)\s*$"
)
_ASSUMPTION_MEM_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(in|not in)\s*([A-Za-z_][A-Za-z0-9_]*)\s*$"
)


def _parse_assumption_to_lean(property_text: str) -> str:
    match = _ASSUMPTION_BINARY_RE.match(property_text.strip())
    if match:
        left, op, right = match.groups()
        op_map = {
            ">=": "≥",
            "<=": "≤",
            ">": ">",
            "<": "<",
            "==": "=",
            "!=": "≠",
        }
        return f"({left} {op_map[op]} {right})"

    mem_match = _ASSUMPTION_MEM_RE.match(property_text.strip())
    if mem_match:
        left, op, right = mem_match.groups()
        symbol = "∈" if op == "in" else "∉"
        return f"({left} {symbol} {right})"

    return ""
