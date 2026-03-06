from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from ..models import Obligation
from .chunker import IRChunk, IRChunker
from .lean_render import render_expr
from .models import (
    IRConcat,
    IRExpr,
    IRFunction,
    IRListLiteral,
    IRProgram,
    IRSubscript,
    IRType,
)


class VCGenerationError(RuntimeError):
    pass


@dataclass(frozen=True)
class VerificationCondition:
    id: str
    theorem_name: str
    obligation: Obligation
    function: IRFunction
    proposition: str
    proof_kind: str


@dataclass(frozen=True)
class VCGenerationOutcome:
    success: bool
    conditions: List[VerificationCondition]
    error: str = ""


class VerificationConditionGenerator:
    def __init__(self) -> None:
        self.chunker = IRChunker()

    def generate(self, program: IRProgram, obligations: List[Obligation]) -> VCGenerationOutcome:
        functions: Dict[str, IRFunction] = {fn.name: fn for fn in program.functions}
        conditions: List[VerificationCondition] = []

        for obligation in obligations:
            fn_name = obligation.id.split(":", 1)[0]
            fn = functions.get(fn_name)
            if fn is None:
                return VCGenerationOutcome(
                    success=False,
                    conditions=[],
                    error=f"Obligation '{obligation.id}' references unknown function '{fn_name}'",
                )

            theorem_name = _sanitize_theorem_name(obligation.id)
            try:
                proposition, proof_kind = self._build_proposition(fn, obligation)
            except VCGenerationError as exc:
                return VCGenerationOutcome(
                    success=False,
                    conditions=[],
                    error=f"{obligation.id}: {exc}",
                )

            conditions.append(
                VerificationCondition(
                    id=obligation.id,
                    theorem_name=theorem_name,
                    obligation=obligation,
                    function=fn,
                    proposition=proposition,
                    proof_kind=proof_kind,
                )
            )

        return VCGenerationOutcome(success=True, conditions=conditions)

    def _build_proposition(self, fn: IRFunction, obligation: Obligation) -> tuple[str, str]:
        args = " ".join(param.name for param in fn.params)
        call_expr = f"{fn.name} {args}".strip()

        if obligation.category == "non_negativity":
            if fn.return_type != IRType.INT:
                raise VCGenerationError(
                    "non_negativity obligation requires Int-returning function"
                )
            return f"({call_expr} ≥ 0)", "non_negativity"

        chunks = self.chunker.chunk_function(fn)
        if obligation.category == "bounds":
            clauses = self._bounds_clauses(chunks)
            if not clauses:
                raise VCGenerationError("No index accesses discovered for bounds obligation")
            return _conjoin(clauses), "bounds"

        if obligation.category == "uniqueness":
            clauses = self._uniqueness_clauses(chunks)
            if not clauses:
                raise VCGenerationError("No append patterns discovered for uniqueness obligation")
            return _conjoin(clauses), "uniqueness"

        raise VCGenerationError(f"Unsupported obligation category '{obligation.category}'")

    def _bounds_clauses(self, chunks: Iterable[IRChunk]) -> List[str]:
        clauses: List[str] = []
        for chunk in chunks:
            for access in self._collect_subscripts(chunk):
                idx = render_expr(access.index)
                coll = render_expr(access.collection)
                bound = f"((0 ≤ {idx}) ∧ ({idx} < Int.ofNat ({coll}.length)))"
                if chunk.path_conditions:
                    pc = _conjoin(render_expr(cond) for cond in chunk.path_conditions)
                    clauses.append(f"(({pc}) → {bound})")
                else:
                    clauses.append(bound)
        return clauses

    def _uniqueness_clauses(self, chunks: Iterable[IRChunk]) -> List[str]:
        clauses: List[str] = []
        for chunk in chunks:
            for concat in self._collect_singleton_appends(chunk):
                left = render_expr(concat.left)
                singleton = concat.right
                if len(singleton.items) != 1:
                    continue
                item = render_expr(singleton.items[0])
                guard = f"({item} ∉ {left})"
                if chunk.path_conditions:
                    pc = _conjoin(render_expr(cond) for cond in chunk.path_conditions)
                    clauses.append(f"(({pc}) → {guard})")
                else:
                    clauses.append(guard)
        return clauses

    def _collect_subscripts(self, chunk: IRChunk) -> List[IRSubscript]:
        nodes: List[IRSubscript] = []
        for binding in chunk.bindings:
            nodes.extend(_find_nodes(binding.value, IRSubscript))
        for cond in chunk.path_conditions:
            nodes.extend(_find_nodes(cond, IRSubscript))
        nodes.extend(_find_nodes(chunk.result, IRSubscript))
        return nodes

    def _collect_singleton_appends(self, chunk: IRChunk) -> List[IRConcat]:
        nodes: List[IRConcat] = []
        for binding in chunk.bindings:
            nodes.extend(_find_nodes(binding.value, IRConcat))
        nodes.extend(_find_nodes(chunk.result, IRConcat))
        out: List[IRConcat] = []
        for node in nodes:
            if isinstance(node.right, IRListLiteral) and len(node.right.items) == 1:
                out.append(node)
        return out


def _sanitize_theorem_name(obligation_id: str) -> str:
    return obligation_id.replace(":", "_").replace("-", "_")


def _conjoin(parts: Iterable[str]) -> str:
    items = [part for part in parts if part]
    if not items:
        return "True"
    if len(items) == 1:
        return items[0]
    return "(" + " ∧ ".join(items) + ")"


def _find_nodes(expr: IRExpr, target_type: type) -> List[IRExpr]:
    out: List[IRExpr] = []

    def walk(node: IRExpr) -> None:
        if isinstance(node, target_type):
            out.append(node)

        from .models import (
            IRBinaryOp,
            IRBoolOp,
            IRCompare,
            IRConcat,
            IRIfThenElse,
            IRLen,
            IRLet,
            IRListLiteral,
            IRSubscript,
            IRUnaryOp,
        )

        if isinstance(node, IRUnaryOp):
            walk(node.operand)
            return
        if isinstance(node, (IRBinaryOp, IRBoolOp, IRCompare, IRConcat)):
            walk(node.left)
            walk(node.right)
            return
        if isinstance(node, IRIfThenElse):
            walk(node.condition)
            walk(node.then_expr)
            walk(node.else_expr)
            return
        if isinstance(node, IRLet):
            walk(node.value)
            walk(node.body)
            return
        if isinstance(node, IRSubscript):
            walk(node.collection)
            walk(node.index)
            return
        if isinstance(node, IRLen):
            walk(node.collection)
            return
        if isinstance(node, IRListLiteral):
            for item in node.items:
                walk(item)

    walk(expr)
    return out
