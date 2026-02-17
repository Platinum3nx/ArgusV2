from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import List

try:
    from google import genai
except Exception:  # pragma: no cover - optional dependency in test envs
    genai = SimpleNamespace(Client=None)

from ..models import AssumedInput, Obligation
from .base import TranslationOutcome


PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "translate_lean_advanced.md"


class LLMTranslator:
    def __init__(self, model: str = "gemini-2.5-pro") -> None:
        self.model = model

    def translate(
        self,
        python_code: str,
        obligations: List[Obligation],
        assumptions: List[AssumedInput],
    ) -> TranslationOutcome:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return TranslationOutcome(
                success=False,
                language="lean",
                code="",
                translator="llm",
                used_llm=True,
                error="GEMINI_API_KEY is not configured",
            )
        if getattr(genai, "Client", None) is None:
            return TranslationOutcome(
                success=False,
                language="lean",
                code="",
                translator="llm",
                used_llm=True,
                error="google-genai is not installed",
            )

        prompt = self._load_prompt()
        obligations_text = "\n".join(f"- {item.property}" for item in obligations) or "- none"
        assumptions_text = "\n".join(f"- {item.property}" for item in assumptions) or "- none"
        contents = (
            f"{prompt}\n\n"
            f"Obligations:\n{obligations_text}\n\n"
            f"Assumptions:\n{assumptions_text}\n\n"
            f"Python Code:\n{python_code}"
        )

        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(model=self.model, contents=contents)
            text = (response.text or "").strip()
            if not text:
                raise RuntimeError("Gemini returned an empty translation")
            return TranslationOutcome(
                success=True,
                language="lean",
                code=text,
                translator="llm",
                used_llm=True,
            )
        except Exception as exc:
            return TranslationOutcome(
                success=False,
                language="lean",
                code="",
                translator="llm",
                used_llm=True,
                error=str(exc),
            )

    def _load_prompt(self) -> str:
        if PROMPT_PATH.exists():
            return PROMPT_PATH.read_text(encoding="utf-8")
        return "Translate Python to Lean 4. Return code only."
from types import SimpleNamespace
