from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .assumption_evidence import ALLOWED_SOURCE_TYPES, validate_assumptions
from .llm_provider import LLMClient
from .models import AssumedInput, Obligation, Severity
from .obligation_policy import ObligationPolicy


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "discover_invariants.md"


@dataclass
class DiscoveryResult:
    obligations: List[Obligation]
    assumed_inputs: List[AssumedInput]
    llm_candidates_raw: str
    assumptions_valid: bool


class InvariantDiscovery:
    def __init__(
        self,
        llm_client: LLMClient | None = None,
        use_llm: bool = True,
    ) -> None:
        self.llm_client = llm_client
        self.use_llm = use_llm and llm_client is not None
        self.policy = ObligationPolicy()

    def discover(self, python_code: str) -> DiscoveryResult:
        policy_result = self.policy.derive(python_code)
        obligations = list(policy_result.obligations)
        assumed_inputs: List[AssumedInput] = []
        raw = ""

        if self.use_llm:
            raw = self._query_llm(python_code)
            assumed_inputs = self._parse_assumptions(raw)

        assumptions_valid, _ = validate_assumptions(assumed_inputs)
        return DiscoveryResult(
            obligations=obligations,
            assumed_inputs=assumed_inputs,
            llm_candidates_raw=raw,
            assumptions_valid=assumptions_valid,
        )

    def _query_llm(self, python_code: str) -> str:
        if self.llm_client is None:
            return ""
        prompt = self._load_prompt()
        try:
            return self.llm_client.generate(f"{prompt}\n\nPython:\n{python_code}")
        except Exception:
            return ""

    def _load_prompt(self) -> str:
        if PROMPT_PATH.exists():
            return PROMPT_PATH.read_text(encoding="utf-8")
        return (
            "Return JSON with `assumed_inputs` and `obligations` candidates. "
            "Do not include markdown fences."
        )

    def _parse_assumptions(self, text: str) -> List[AssumedInput]:
        if not text:
            return []
        payload = _extract_json(text)
        if not payload:
            return []

        assumptions: List[AssumedInput] = []
        for item in payload.get("assumed_inputs", []):
            if not isinstance(item, dict):
                continue
            prop = str(item.get("property", "")).strip()
            if not prop:
                # Drop LLM assumptions with empty property — they can't
                # contribute to formal verification and fail evidence validation.
                continue
            source_type = str(item.get("source_type", "")).strip()
            if source_type not in ALLOWED_SOURCE_TYPES:
                # Drop assumptions whose source_type the evidence validator
                # would reject. Deterministic preconditions are always valid.
                continue
            if _is_inter_parameter_constraint(prop):
                # Drop constraints that compare two named variables (e.g. "balance >= amount").
                # Such guards must exist in the code to be sound. If they are missing the
                # code is VULNERABLE. Accepting them as LLM assumptions would cause false
                # VERIFIED verdicts — the exact opposite of fail-closed.
                continue
            assumptions.append(
                AssumedInput(
                    property=prop,
                    description=str(item.get("description", "")).strip(),
                    justification=str(item.get("justification", "")).strip(),
                    source_type=source_type,
                    source_ref=str(item.get("source_ref", "")).strip(),
                    evidence_id=str(item.get("evidence_id", "")).strip(),
                    severity=Severity(str(item.get("severity", "medium")).lower())
                    if str(item.get("severity", "medium")).lower() in {s.value for s in Severity}
                    else Severity.MEDIUM,
                )
            )
        return assumptions


def _is_inter_parameter_constraint(prop: str) -> bool:
    """Return True if the property compares two named variables.

    Constraints such as "balance >= amount" represent business-logic guards that
    MUST exist in the code to be meaningful.  Accepting them as LLM assumptions
    would allow a hallucinated guard to make a vulnerable function appear verified.
    Properties comparing a variable to a constant ("amount >= 0") are fine.
    """
    pattern = re.compile(r"\b([A-Za-z_]\w*)\s*(?:>=|<=|>|<|==|!=)\s*([A-Za-z_]\w*)\b")
    match = pattern.search(prop)
    if not match:
        return False
    lhs, rhs = match.group(1), match.group(2)
    _SAFE_LITERALS = {"True", "False", "None"}
    return lhs not in _SAFE_LITERALS and rhs not in _SAFE_LITERALS


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text)
    text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return {}
