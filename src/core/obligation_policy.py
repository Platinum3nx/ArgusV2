from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import dataclass
from typing import List, Set

from .models import AssumedInput, Obligation, Severity


NUMERIC_HINT_NAMES = {"balance", "amount", "total", "count", "value"}
STATE_HINT_NAMES = {"state", "status", "level"}


@dataclass
class ObligationPolicyResult:
    obligations: List[Obligation]
    unsupported_constructs: List[str]

    def canonical_hash(self) -> str:
        payload = [item.to_dict() for item in sorted(self.obligations, key=lambda x: x.id)]
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ObligationPolicy:
    """
    Deterministic canonical obligation generation.

    LLM output is advisory; pass criteria are produced here.
    """

    def derive(self, python_code: str) -> ObligationPolicyResult:
        try:
            tree = ast.parse(python_code)
        except SyntaxError:
            return ObligationPolicyResult(
                obligations=[],
                unsupported_constructs=["syntax_error"],
            )

        obligations: List[Obligation] = []
        unsupported: Set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                unsupported.add("async_function")
            if isinstance(node, ast.ClassDef):
                unsupported.add("class_definition")
            if isinstance(node, ast.Yield):
                unsupported.add("generator_yield")
            if isinstance(node, ast.Await):
                unsupported.add("await_expression")

        for fn in [item for item in tree.body if isinstance(item, ast.FunctionDef)]:
            obligations.extend(self._derive_function_obligations(fn))

        unique = {item.id: item for item in obligations}
        return ObligationPolicyResult(
            obligations=[unique[key] for key in sorted(unique.keys())],
            unsupported_constructs=sorted(unsupported),
        )

    def _derive_function_obligations(self, fn: ast.FunctionDef) -> List[Obligation]:
        obligations: List[Obligation] = []
        param_names = [arg.arg for arg in fn.args.args]
        param_set = {name.lower() for name in param_names}
        body_nodes = [node for stmt in fn.body for node in ast.walk(stmt)]
        returns_numeric = self._returns_numeric(fn)

        has_loop = any(isinstance(node, (ast.For, ast.While)) for node in body_nodes)
        has_subscript = any(isinstance(node, ast.Subscript) for node in body_nodes)
        has_minus = any(
            isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub)
            for node in body_nodes
        )
        has_list_append = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "append"
            for node in body_nodes
        )
        has_concat_append = any(
            isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.Add)
            and isinstance(node.right, ast.List)
            and len(node.right.elts) == 1
            for node in body_nodes
        )
        has_state_hint = bool(param_set.intersection(STATE_HINT_NAMES))

        if returns_numeric and (has_minus or param_set.intersection(NUMERIC_HINT_NAMES)):
            obligations.append(
                Obligation(
                    id=f"{fn.name}:non_negative_result",
                    property=f"{fn.name}(...) >= 0",
                    category="non_negativity",
                    description="Result should remain non-negative under validated inputs",
                    severity=Severity.CRITICAL,
                )
            )

        if has_subscript:
            obligations.append(
                Obligation(
                    id=f"{fn.name}:bounds_safe_access",
                    property="All index operations are bounds-safe",
                    category="bounds",
                    description="Indexing operations must not access out-of-range elements",
                    severity=Severity.CRITICAL,
                )
            )

        if has_list_append or has_concat_append:
            obligations.append(
                Obligation(
                    id=f"{fn.name}:preserve_uniqueness",
                    property="Collection updates preserve uniqueness where required",
                    category="uniqueness",
                    description="List/set update patterns should avoid duplicate insertion",
                    severity=Severity.HIGH,
                )
            )

        if has_loop:
            obligations.append(
                Obligation(
                    id=f"{fn.name}:loop_progress_and_safety",
                    property="Loop preserves invariants and terminates",
                    category="loop_invariant",
                    description="Loop variables should stay in valid ranges with valid progress",
                    severity=Severity.HIGH,
                )
            )

        if has_state_hint:
            obligations.append(
                Obligation(
                    id=f"{fn.name}:valid_state_transition",
                    property="State transitions remain within policy",
                    category="state_transition",
                    description="State-like values must follow allowed transition rules",
                    severity=Severity.HIGH,
                )
            )

        return obligations

    def derive_preconditions(self, python_code: str, obligations: List[Obligation]) -> List[AssumedInput]:
        """
        Deterministically derive precondition assumptions for non_negativity obligations.

        For each function with a non_negativity obligation, injects ``param >= 0``
        for every int-annotated parameter. These assumptions become Lean hypotheses
        regardless of LLM availability, ensuring proofs can discharge the obligation.
        """
        try:
            tree = ast.parse(python_code)
        except SyntaxError:
            return []

        fn_map = {
            node.name: node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
        }

        preconditions: List[AssumedInput] = []
        seen: set[str] = set()

        for obligation in obligations:
            if obligation.category != "non_negativity":
                continue
            fn_name = obligation.id.split(":", 1)[0]
            fn = fn_map.get(fn_name)
            if fn is None:
                continue

            for arg in fn.args.args:
                if not self._is_int_param(arg):
                    continue
                prop = f"{arg.arg} >= 0"
                if prop in seen:
                    continue
                seen.add(prop)
                preconditions.append(
                    AssumedInput(
                        property=prop,
                        description=f"Parameter '{arg.arg}' is non-negative (domain precondition)",
                        justification="Derived deterministically from non_negativity obligation on function parameters",
                        source_type="policy",
                        source_ref="obligation_policy:derive_preconditions",
                        evidence_id=f"precond:{fn_name}:{arg.arg}:non_negative",
                        severity=Severity.HIGH,
                    )
                )

        return preconditions

    def _is_int_param(self, arg: ast.arg) -> bool:
        if arg.annotation is None:
            return True  # default to int assumption when unannotated
        if isinstance(arg.annotation, ast.Name):
            return arg.annotation.id in {"int", "Int"}
        return False

    def _returns_numeric(self, fn: ast.FunctionDef) -> bool:
        if fn.returns is None:
            return True
        if isinstance(fn.returns, ast.Name):
            return fn.returns.id in {"int", "float", "Int", "Float"}
        return False
