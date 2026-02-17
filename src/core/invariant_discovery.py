from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from google import genai

from .assumption_evidence import validate_assumptions
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
        model: str = "gemini-2.5-pro",
        use_llm: bool = True,
    ) -> None:
        self.model = model
        self.use_llm = use_llm
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
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return ""

        prompt = self._load_prompt()
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=f"{prompt}\n\nPython:\n{python_code}",
        )
        return (response.text or "").strip()

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
            assumptions.append(
                AssumedInput(
                    property=str(item.get("property", "")).strip(),
                    description=str(item.get("description", "")).strip(),
                    justification=str(item.get("justification", "")).strip(),
                    source_type=str(item.get("source_type", "")).strip() or "policy",
                    source_ref=str(item.get("source_ref", "")).strip(),
                    evidence_id=str(item.get("evidence_id", "")).strip(),
                    severity=Severity(str(item.get("severity", "medium")).lower())
                    if str(item.get("severity", "medium")).lower() in {s.value for s in Severity}
                    else Severity.MEDIUM,
                )
            )
        return assumptions


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

