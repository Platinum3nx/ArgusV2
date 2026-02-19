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

    if not obligations:
        issues.append(
            SemanticGuardIssue(
                code="NO_OBLIGATIONS",
                message="Canonical obligation set is empty",
            )
        )

    if _contains_sorry(translated_code):
        issues.append(
            SemanticGuardIssue(
                code="PROOF_SORRY",
                message="Translated proof contains `sorry`",
            )
        )

    if "unsupported" in translated_code.lower():
        issues.append(
            SemanticGuardIssue(
                code="UNSUPPORTED_MARKER",
                message="Translated artifact contains unsupported marker",
            )
        )

    source_function_names = _extract_python_function_names(python_code)
    for fn in sorted(source_function_names):
        if not _contains_function_symbol(translated_code, fn):
            issues.append(
                SemanticGuardIssue(
                    code="MISSING_FUNCTION_SYMBOL",
                    message=f"Translated artifact missing function symbol '{fn}'",
                )
            )

    for obligation in obligations:
        if obligation.category == "uniqueness":
            if "Nodup" not in translated_code and "no_duplicates" not in translated_code:
                issues.append(
                    SemanticGuardIssue(
                        code="WEAK_UNIQUENESS_ENCODING",
                        message=f"Obligation '{obligation.id}' appears unencoded in proof artifact",
                    )
                )
        if obligation.category == "bounds":
            if ("<" not in translated_code and "≤" not in translated_code) and "index" not in translated_code:
                issues.append(
                    SemanticGuardIssue(
                        code="WEAK_BOUNDS_ENCODING",
                        message=f"Obligation '{obligation.id}' appears unencoded in proof artifact",
                    )
                )
        if obligation.category == "non_negativity":
            if "≥ 0" not in translated_code and ">= 0" not in translated_code:
                issues.append(
                    SemanticGuardIssue(
                        code="WEAK_NONNEG_ENCODING",
                        message=f"Obligation '{obligation.id}' appears unencoded in proof artifact",
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
    no_comments = re.sub(r"--.*$", "", code, flags=re.MULTILINE)
    return re.search(r"\bsorry\b", no_comments) is not None

