from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .llm_provider import LLMClient
from .ir.lowerer import PythonIRLowerer
from .models import Obligation


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "repair_code.md"
_CODE_BLOCK_RE = re.compile(
    r"```(?:[A-Za-z0-9_+-]+)?\s*\n(.*?)\n```",
    flags=re.IGNORECASE | re.DOTALL,
)


@dataclass
class RepairAttempt:
    attempt: int
    fixed_code: str
    success: bool
    error: str = ""


@dataclass
class RepairResult:
    attempts: List[RepairAttempt]
    fixed_code: str | None
    success: bool


class RepairEngine:
    def __init__(self, llm_client: LLMClient, max_attempts: int = 3) -> None:
        self.llm_client = llm_client
        self.max_attempts = max_attempts
        self.lowerer = PythonIRLowerer()

    def repair(self, python_code: str, error_message: str, obligations: List[Obligation]) -> RepairResult:
        attempts: List[RepairAttempt] = []
        current_context = error_message

        for attempt in range(1, self.max_attempts + 1):
            fixed, err = self._generate_fix(python_code, current_context, obligations)
            ok = bool(fixed) and not err
            attempts.append(
                RepairAttempt(
                    attempt=attempt,
                    fixed_code=fixed or "",
                    success=ok,
                    error=err,
                )
            )
            if ok:
                return RepairResult(attempts=attempts, fixed_code=fixed, success=True)
            current_context = f"{current_context}\nPrevious attempt failed validation: {err}"

        return RepairResult(attempts=attempts, fixed_code=None, success=False)

    def _generate_fix(
        self, python_code: str, error_message: str, obligations: List[Obligation]
    ) -> tuple[str | None, str]:
        obligations_text = "\n".join(f"- {item.property}" for item in obligations) or "- none"
        prompt = self._load_prompt()
        contents = (
            f"{prompt}\n\n"
            f"Obligations:\n{obligations_text}\n\n"
            f"Verification error:\n{error_message}\n\n"
            f"Python code:\n{python_code}"
        )
        try:
            fixed_code = self.llm_client.generate(contents)
        except Exception as exc:
            return None, str(exc)

        sanitized = self._extract_python_code(fixed_code)
        if not sanitized:
            return None, f"{self.llm_client.provider_name} returned empty fix"

        valid, reason = self._validate_fix(python_code, sanitized)
        if not valid:
            return None, reason

        return sanitized, ""

    def _load_prompt(self) -> str:
        if PROMPT_PATH.exists():
            return PROMPT_PATH.read_text(encoding="utf-8")
        return "Fix the Python code so all obligations are satisfied. Return code only."

    def _extract_python_code(self, text: str) -> str:
        stripped = text.strip()
        if not stripped:
            return ""

        match = _CODE_BLOCK_RE.search(stripped)
        if match:
            return match.group(1).strip()

        return stripped

    def _validate_fix(self, original_code: str, candidate_code: str) -> tuple[bool, str]:
        try:
            original_tree = ast.parse(original_code)
        except SyntaxError as exc:
            return False, f"Original code is invalid: {exc}"

        try:
            candidate_tree = ast.parse(candidate_code)
        except SyntaxError as exc:
            return False, f"Repair output is not valid Python: {exc}"

        original_functions = self._top_level_function_signatures(original_tree)
        candidate_functions = self._top_level_function_signatures(candidate_tree)
        if not candidate_functions:
            return False, "Repair output did not contain any top-level function definitions"

        if len(original_functions) != len(candidate_functions):
            return False, "Repair output changed the number of top-level function definitions"

        for original, candidate in zip(original_functions, candidate_functions):
            if original["name"] != candidate["name"]:
                return False, f"Repair output changed top-level function '{original['name']}'"
            if original != candidate:
                return False, f"Repair output changed signature for function '{original['name']}'"

        lowered = self.lowerer.lower(candidate_code)
        if not lowered.success:
            reason = lowered.error or ", ".join(lowered.unsupported_constructs) or "unsupported Python subset"
            return False, f"Repair output uses unsupported Python subset: {reason}"

        return True, ""

    def _top_level_function_signatures(self, tree: ast.AST) -> list[dict[str, object]]:
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        signatures: list[dict[str, object]] = []
        for fn in functions:
            signatures.append(
                {
                    "name": fn.name,
                    "posonlyargs": [self._arg_signature(arg) for arg in fn.args.posonlyargs],
                    "args": [self._arg_signature(arg) for arg in fn.args.args],
                    "vararg": self._arg_signature(fn.args.vararg) if fn.args.vararg else None,
                    "kwonlyargs": [self._arg_signature(arg) for arg in fn.args.kwonlyargs],
                    "kwarg": self._arg_signature(fn.args.kwarg) if fn.args.kwarg else None,
                    "defaults": [ast.unparse(item) for item in fn.args.defaults],
                    "kw_defaults": [
                        ast.unparse(item) if item is not None else None for item in fn.args.kw_defaults
                    ],
                    "returns": ast.unparse(fn.returns) if fn.returns is not None else None,
                }
            )
        return signatures

    def _arg_signature(self, arg: ast.arg | None) -> tuple[str, str | None] | None:
        if arg is None:
            return None
        annotation = ast.unparse(arg.annotation) if arg.annotation is not None else None
        return (arg.arg, annotation)
