from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Verdict(str, Enum):
    VERIFIED = "VERIFIED"
    FIXED = "FIXED"
    VULNERABLE = "VULNERABLE"
    UNVERIFIED = "UNVERIFIED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class Obligation:
    id: str
    property: str
    category: str
    description: str
    severity: Severity = Severity.HIGH
    source: str = "policy"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass(frozen=True)
class AssumedInput:
    property: str
    description: str
    justification: str
    source_type: str
    source_ref: str
    evidence_id: str
    severity: Severity = Severity.MEDIUM

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass(frozen=True)
class ObligationResult:
    obligation: Obligation
    verified: bool
    engine: str
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "obligation": self.obligation.to_dict(),
            "verified": self.verified,
            "engine": self.engine,
            "message": self.message,
        }


@dataclass
class VerificationSummary:
    obligation_results: List[ObligationResult]
    assumptions_valid: bool
    unsupported_constructs: List[str]
    semantic_guard_passed: bool
    verification_error: bool = False
    repaired: bool = False
    details: Dict[str, Any] | None = None

    @property
    def all_obligations_passed(self) -> bool:
        return bool(self.obligation_results) and all(
            item.verified for item in self.obligation_results
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "obligation_results": [item.to_dict() for item in self.obligation_results],
            "assumptions_valid": self.assumptions_valid,
            "unsupported_constructs": self.unsupported_constructs,
            "semantic_guard_passed": self.semantic_guard_passed,
            "verification_error": self.verification_error,
            "repaired": self.repaired,
            "details": self.details or {},
            "all_obligations_passed": self.all_obligations_passed,
        }

