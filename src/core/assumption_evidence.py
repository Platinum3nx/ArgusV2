from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from .models import AssumedInput


ALLOWED_SOURCE_TYPES = {
    "api_schema",
    "db_constraint",
    "validator",
    "policy",
    "runtime_guard",
}


@dataclass(frozen=True)
class EvidenceIssue:
    property: str
    reason: str


def validate_assumptions(assumptions: Iterable[AssumedInput]) -> Tuple[bool, List[EvidenceIssue]]:
    issues: List[EvidenceIssue] = []
    seen_properties: set[str] = set()

    for assumption in assumptions:
        prop = assumption.property.strip()
        if not prop:
            issues.append(EvidenceIssue(property="<empty>", reason="Missing property"))
            continue

        if prop in seen_properties:
            issues.append(EvidenceIssue(property=prop, reason="Duplicate assumption property"))
        seen_properties.add(prop)

        if assumption.source_type not in ALLOWED_SOURCE_TYPES:
            issues.append(
                EvidenceIssue(
                    property=prop,
                    reason=f"Unsupported source_type '{assumption.source_type}'",
                )
            )

        if not assumption.justification.strip():
            issues.append(EvidenceIssue(property=prop, reason="Missing justification"))
        if not assumption.source_ref.strip():
            issues.append(EvidenceIssue(property=prop, reason="Missing source_ref"))
        if not assumption.evidence_id.strip():
            issues.append(EvidenceIssue(property=prop, reason="Missing evidence_id"))

    return len(issues) == 0, issues

