from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import List

from .models import Obligation


@dataclass(frozen=True)
class SemanticGuardIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SemanticGuardResult:
    passed: bool
    issues: List[SemanticGuardIssue]


def run_semantic_guard(
    python_code: str, translated_code: str, obligations: List[Obligation]
) -> SemanticGuardResult:
    issues: List[SemanticGuardIssue] = []
    stripped = _strip_comments(translated_code)

    if not obligations:
        issues.append(
            SemanticGuardIssue(
                code="NO_OBLIGATIONS",
                message="Canonical obligation set is empty",
            )
        )

    if _contains_sorry(stripped):
        issues.append(
            SemanticGuardIssue(
                code="PROOF_SORRY",
                message="Translated proof contains `sorry`",
            )
        )

    if "unsupported" in stripped.lower():
        issues.append(
            SemanticGuardIssue(
                code="UNSUPPORTED_MARKER",
                message="Translated artifact contains unsupported marker",
            )
        )

    source_function_names = _extract_python_function_names(python_code)
    for fn in sorted(source_function_names):
        if not _contains_function_symbol(stripped, fn):
            issues.append(
                SemanticGuardIssue(
                    code="MISSING_FUNCTION_SYMBOL",
                    message=f"Translated artifact missing function symbol '{fn}'",
                )
            )

    is_lean = bool(re.search(r"\btheorem\b|\bdef\b", stripped))
    is_dafny = bool(re.search(r"\bmethod\b", stripped))

    if obligations and not is_lean and not is_dafny:
        issues.append(
            SemanticGuardIssue(
                code="UNRECOGNIZED_TRANSLATION_FORMAT",
                message="Translated code matches neither Lean nor Dafny patterns",
            )
        )

    for obligation in obligations:
        theorem_name = _obligation_theorem_name(obligation.id)
        fn_name = obligation.id.split(":", 1)[0]

        if is_lean:
            theorem_goal = _extract_theorem_goal(stripped, theorem_name)
            if theorem_goal is None:
                issues.append(
                    SemanticGuardIssue(
                        code="MISSING_OBLIGATION_THEOREM",
                        message=f"Missing theorem '{theorem_name}' for obligation '{obligation.id}'",
                    )
                )
                continue

            if _is_trivial_goal(theorem_goal):
                issues.append(
                    SemanticGuardIssue(
                        code="TRIVIAL_THEOREM_GOAL",
                        message=f"Theorem '{theorem_name}' has trivial goal '{theorem_goal}'",
                    )
                )

            if obligation.category == "uniqueness":
                if "Nodup" not in theorem_goal and "∉" not in theorem_goal:
                    issues.append(
                        SemanticGuardIssue(
                            code="WEAK_UNIQUENESS_ENCODING",
                            message=f"Obligation '{obligation.id}' appears weakly encoded in theorem goal",
                        )
                    )
            elif obligation.category == "bounds":
                if "length" not in theorem_goal or ("≤" not in theorem_goal and "<" not in theorem_goal):
                    issues.append(
                        SemanticGuardIssue(
                            code="WEAK_BOUNDS_ENCODING",
                            message=f"Obligation '{obligation.id}' appears weakly encoded in theorem goal",
                        )
                    )
            elif obligation.category == "non_negativity":
                if ("≥ 0" not in theorem_goal and ">= 0" not in theorem_goal) or fn_name not in theorem_goal:
                    issues.append(
                        SemanticGuardIssue(
                            code="WEAK_NONNEG_ENCODING",
                            message=f"Obligation '{obligation.id}' appears weakly encoded in theorem goal",
                        )
                    )

        elif is_dafny:
            signature = _extract_dafny_method_signature(stripped, fn_name)
            if signature is None:
                issues.append(
                    SemanticGuardIssue(
                        code="MISSING_OBLIGATION_METHOD",
                        message=f"Missing method '{fn_name}' for obligation '{obligation.id}'",
                    )
                )
                continue

            ensures = _extract_dafny_ensures(signature)
            if obligation.category == "non_negativity":
                if not any("result >= 0" in item for item in ensures):
                    issues.append(
                        SemanticGuardIssue(
                            code="WEAK_NONNEG_ENCODING",
                            message=f"Obligation '{obligation.id}' missing Dafny ensures result >= 0",
                        )
                    )
            elif obligation.category == "loop_invariant":
                if "invariant" not in stripped or "decreases" not in stripped:
                    issues.append(
                        SemanticGuardIssue(
                            code="WEAK_LOOP_ENCODING",
                            message=f"Obligation '{obligation.id}' missing loop invariant/decreases clauses",
                        )
                    )
            elif obligation.category == "bounds":
                if not any("result >= 0" in item or "length" in item for item in ensures):
                    issues.append(
                        SemanticGuardIssue(
                            code="WEAK_BOUNDS_ENCODING",
                            message=f"Obligation '{obligation.id}' missing Dafny bounds encoding",
                        )
                    )
            elif obligation.category == "uniqueness":
                if not any("distinct" in item.lower() or "!in" in item.lower() for item in ensures):
                    issues.append(
                        SemanticGuardIssue(
                            code="WEAK_UNIQUENESS_ENCODING",
                            message=f"Obligation '{obligation.id}' missing Dafny uniqueness encoding",
                        )
                    )

    return SemanticGuardResult(passed=len(issues) == 0, issues=issues)


def _extract_python_function_names(code: str) -> set[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()
    return {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}


def _contains_function_symbol(translated_code: str, fn: str) -> bool:
    pattern = rf"\b(def|theorem|lemma|method)\s+{re.escape(fn)}\b"
    return re.search(pattern, translated_code) is not None


def _contains_sorry(code: str) -> bool:
    return re.search(r"\bsorry\b", code) is not None


def _strip_comments(code: str) -> str:
    no_line_comments = re.sub(r"--.*$", "", code, flags=re.MULTILINE)
    return re.sub(r"/\-.*?\-/", "", no_line_comments, flags=re.DOTALL)


def _obligation_theorem_name(obligation_id: str) -> str:
    return obligation_id.replace(":", "_").replace("-", "_")


def _extract_theorem_goal(code: str, theorem_name: str) -> str | None:
    pattern = rf"\btheorem\s+{re.escape(theorem_name)}\b([\s\S]*?)\s:=\s*by"
    match = re.search(pattern, code)
    if not match:
        return None
    header = match.group(1)
    if ":" not in header:
        return None
    return header.rsplit(":", 1)[1].strip()


def _is_trivial_goal(goal: str) -> bool:
    normalized = goal.replace(" ", "").replace("(", "").replace(")", "")
    return normalized == "True"


def _extract_dafny_method_signature(code: str, fn_name: str) -> str | None:
    pattern = rf"\bmethod\s+{re.escape(fn_name)}\b([\s\S]*?)\{{"
    match = re.search(pattern, code)
    if not match:
        return None
    return match.group(1)


def _extract_dafny_ensures(signature: str) -> List[str]:
    return re.findall(r"^\s*ensures\s+(.+)$", signature, flags=re.MULTILINE)
