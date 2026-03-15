from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .llm_provider import LLMClient
from .models import Obligation


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "repair_code.md"


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
            current_context = f"{current_context}\nPrevious attempt failed: {err}"

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
            if not fixed_code:
                return None, f"{self.llm_client.provider_name} returned empty fix"
            return fixed_code, ""
        except Exception as exc:
            return None, str(exc)

    def _load_prompt(self) -> str:
        if PROMPT_PATH.exists():
            return PROMPT_PATH.read_text(encoding="utf-8")
        return "Fix the Python code so all obligations are satisfied. Return code only."
