from __future__ import annotations

from pathlib import Path
from typing import List

from ..llm_provider import LLMClient
from ..models import AssumedInput, Obligation
from .base import TranslationOutcome


PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "translate_lean_advanced.md"


class LLMTranslator:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def translate(
        self,
        python_code: str,
        obligations: List[Obligation],
        assumptions: List[AssumedInput],
    ) -> TranslationOutcome:
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
            text = self.llm_client.generate(contents)
            if not text:
                raise RuntimeError(
                    f"{self.llm_client.provider_name} returned an empty translation"
                )
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
