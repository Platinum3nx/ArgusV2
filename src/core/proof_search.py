from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .llm_provider import LLMClient
from .models import Obligation


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "proof_search.md"


@dataclass(frozen=True)
class ProofAttempt:
    attempt: int
    success: bool
    reason: str
    candidate_code: str = ""


@dataclass(frozen=True)
class ProofSearchResult:
    success: bool
    proof_code: str | None
    attempts: List[ProofAttempt]


class ProofSearchEngine:
    def __init__(self, llm_client: LLMClient, max_attempts: int = 3) -> None:
        self.llm_client = llm_client
        self.max_attempts = max_attempts

    def search(
        self,
        lean_code: str,
        obligations: List[Obligation],
        verifier_error: str,
    ) -> ProofSearchResult:
        attempts: List[ProofAttempt] = []

        prompt = self._load_prompt()
        obligations_text = "\n".join(f"- {item.property}" for item in obligations) or "- none"
        context = (
            f"{prompt}\n\n"
            f"Obligations:\n{obligations_text}\n\n"
            f"Verifier error:\n{verifier_error}\n\n"
            f"Lean code:\n{lean_code}"
        )

        for attempt in range(1, self.max_attempts + 1):
            candidate, error = self._generate_candidate(context)
            if error:
                attempts.append(ProofAttempt(attempt=attempt, success=False, reason=error))
                continue

            ok, reason = self.validate_candidate(lean_code, candidate)
            attempts.append(
                ProofAttempt(
                    attempt=attempt,
                    success=ok,
                    reason=reason,
                    candidate_code=candidate,
                )
            )
            if ok:
                return ProofSearchResult(success=True, proof_code=candidate, attempts=attempts)

        return ProofSearchResult(success=False, proof_code=None, attempts=attempts)

    def validate_candidate(self, original_code: str, candidate_code: str) -> tuple[bool, str]:
        if not candidate_code.strip():
            return False, "Candidate proof is empty"

        # Strip Lean single-line comments before checking for forbidden markers
        code_no_comments = re.sub(r"--.*$", "", candidate_code, flags=re.MULTILINE)
        lowered = code_no_comments.lower()
        if re.search(r"\b(sorry|admit|axiom)\b", lowered):
            return False, "Candidate contains forbidden proof bypass marker"

        orig_prefix = _pre_theorem_prefix(original_code)
        cand_prefix = _pre_theorem_prefix(candidate_code)
        if _normalize_ws(orig_prefix) != _normalize_ws(cand_prefix):
            return False, "Candidate modified function definitions or pre-theorem content"

        original_headers = _extract_theorem_headers(original_code)
        candidate_headers = _extract_theorem_headers(candidate_code)
        if set(original_headers.keys()) != set(candidate_headers.keys()):
            return False, "Candidate changed theorem set"

        for name, header in original_headers.items():
            other = candidate_headers.get(name, "")
            if _normalize_ws(header) != _normalize_ws(other):
                return False, f"Candidate modified theorem header/goal for '{name}'"

        return True, "Candidate preserved theorem/function structure"

    def _generate_candidate(self, context: str) -> tuple[str, str]:
        try:
            text = self.llm_client.generate(context)
            if not text:
                return "", f"{self.llm_client.provider_name} returned empty proof candidate"
            return text, ""
        except Exception as exc:
            return "", str(exc)

    def _load_prompt(self) -> str:
        if PROMPT_PATH.exists():
            return PROMPT_PATH.read_text(encoding="utf-8")
        return (
            "Repair Lean proofs only. Preserve function/theorem headers exactly. "
            "Do not use sorry/admit/axiom."
        )


def _extract_theorem_headers(code: str) -> dict[str, str]:
    pattern = re.compile(r"\btheorem\s+([A-Za-z0-9_']+)\b([\s\S]*?)\s:=\s*by")
    out: dict[str, str] = {}
    for match in pattern.finditer(code):
        name = match.group(1)
        header = f"theorem {name}{match.group(2)}"
        out[name] = header
    return out


def _pre_theorem_prefix(code: str) -> str:
    if "theorem" not in code:
        return code
    return code.split("theorem", 1)[0]


def _normalize_ws(text: str) -> str:
    return " ".join(text.split())
