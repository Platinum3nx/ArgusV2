from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import List

try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency in test envs
    genai = SimpleNamespace(Client=None)

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
    def __init__(self, model: str = "gemini-2.5-pro", max_attempts: int = 3) -> None:
        self.model = model
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
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None, "GEMINI_API_KEY is not configured"
        if getattr(genai, "Client", None) is None:
            return None, "google-genai is not installed"

        obligations_text = "\n".join(f"- {item.property}" for item in obligations) or "- none"
        prompt = self._load_prompt()
        contents = (
            f"{prompt}\n\n"
            f"Obligations:\n{obligations_text}\n\n"
            f"Verification error:\n{error_message}\n\n"
            f"Python code:\n{python_code}"
        )
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(model=self.model, contents=contents)
            fixed_code = (response.text or "").strip()
            if not fixed_code:
                return None, "Gemini returned empty fix"
            return fixed_code, ""
        except Exception as exc:
            return None, str(exc)

    def _load_prompt(self) -> str:
        if PROMPT_PATH.exists():
            return PROMPT_PATH.read_text(encoding="utf-8")
        return "Fix the Python code so all obligations are satisfied. Return code only."
from types import SimpleNamespace
