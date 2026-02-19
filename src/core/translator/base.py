from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from ..models import AssumedInput, Obligation


@dataclass(frozen=True)
class TranslationOutcome:
    success: bool
    language: str
    code: str
    translator: str
    used_llm: bool = False
    error: str = ""


class Translator(Protocol):
    def translate(
        self,
        python_code: str,
        obligations: List[Obligation],
        assumptions: List[AssumedInput],
    ) -> TranslationOutcome:
        ...

