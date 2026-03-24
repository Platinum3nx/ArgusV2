from __future__ import annotations

import re
from pathlib import Path
from typing import List

from ..llm_provider import LLMClient
from ..models import AssumedInput, Obligation
from .base import TranslationOutcome


PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "translate_lean_advanced.md"
LEAN_SIGNAL_RE = re.compile(
    r"\b(?:import|open|namespace|section|variable|variables|def|theorem|lemma|example|abbrev|structure|inductive|instance|axiom|opaque|notation)\b",
    re.IGNORECASE,
)
LEAN_DECLARATION_LINE_RE = re.compile(
    r"^\s*(?:import|open|namespace|section|variable|variables|def|theorem|lemma|example|abbrev|structure|inductive|instance|axiom|opaque|notation)\b",
    re.IGNORECASE,
)
LEAN_TACTIC_LINE_RE = re.compile(
    r"^\s*(?:by|have|show|let|match|exact|simp|simpa|omega|linarith|split_ifs|intro|apply|cases|constructor|refine|rw|dsimp|rfl|aesop|tauto|norm_num|ring_nf)\b",
    re.IGNORECASE,
)
FENCED_BLOCK_RE = re.compile(
    r"```(?P<lang>[A-Za-z0-9_-]*)\s*\n(?P<body>.*?)\n```",
    re.DOTALL,
)


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
            cleaned = self._sanitize_lean_output(text)
            if not cleaned:
                raise RuntimeError(
                    f"{self.llm_client.provider_name} returned no usable Lean code"
                )
            return TranslationOutcome(
                success=True,
                language="lean",
                code=cleaned,
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

    def _sanitize_lean_output(self, text: str) -> str:
        """
        Extract the first usable Lean snippet from an LLM response.

        The translator accepts fenced code blocks and lightly wrapped answers,
        but returns only Lean source text to downstream verification stages.
        """
        candidate = text.replace("\r\n", "\n").strip()
        if not candidate:
            return ""

        fenced = self._extract_fenced_block(candidate)
        if fenced is not None:
            candidate = fenced.strip()

        lines = candidate.splitlines()
        start = self._find_code_start(lines)
        if start is None:
            return ""

        end = self._find_code_end(lines, start)
        if end < start:
            return ""

        cleaned = "\n".join(lines[start : end + 1]).strip()
        if not LEAN_SIGNAL_RE.search(cleaned):
            return ""
        return cleaned

    def _extract_fenced_block(self, text: str) -> str | None:
        matches = list(FENCED_BLOCK_RE.finditer(text))
        if not matches:
            return None
        preferred = (
            match
            for match in matches
            if match.group("lang").lower() in {"lean", "lean4", "lean-4", "lean_4"}
        )
        match = next(preferred, matches[0])
        return match.group("body")

    def _find_code_start(self, lines: list[str]) -> int | None:
        for index, line in enumerate(lines):
            if self._looks_like_lean_code_line(line, allow_tactic_prefix=False):
                return index
        return None

    def _find_code_end(self, lines: list[str], start: int) -> int:
        end = start
        for index in range(start, len(lines)):
            if self._looks_like_lean_code_line(lines[index], allow_tactic_prefix=True):
                end = index
        return end

    def _looks_like_lean_code_line(self, line: str, allow_tactic_prefix: bool) -> bool:
        stripped = line.strip()
        if not stripped:
            return True
        if stripped.startswith(("```", "Here ", "Here:", "Certainly", "Sure", "Explanation", "Below", "Note:")):
            return False
        if stripped.startswith(("--", "/-")):
            return True
        if LEAN_DECLARATION_LINE_RE.match(stripped):
            return True
        if line[:1].isspace():
            return True
        if stripped[0] in {"|", "⟨", "⟩", "(", ")", "{", "}", "[", "]", ":", "=", ",", "."}:
            return True
        if allow_tactic_prefix and LEAN_TACTIC_LINE_RE.match(stripped):
            return True
        return False
