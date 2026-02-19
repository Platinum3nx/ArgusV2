from __future__ import annotations

from dataclasses import dataclass

from .models import VerificationSummary, Verdict


@dataclass(frozen=True)
class VerdictDecision:
    verdict: Verdict
    reason: str


def compute_verdict(summary: VerificationSummary) -> VerdictDecision:
    """
    Fail-closed verdict contract:
    - ERROR on verifier/runtime errors
    - UNVERIFIED on unsupported semantics, missing assumption evidence, or failed guards
    - VERIFIED/FIXED only when all obligations pass
    - VULNERABLE otherwise
    """
    if summary.verification_error:
        return VerdictDecision(Verdict.ERROR, "Verification runtime/tooling error")

    if summary.unsupported_constructs:
        return VerdictDecision(
            Verdict.UNVERIFIED,
            "Unsupported constructs encountered: "
            + ", ".join(sorted(summary.unsupported_constructs)),
        )

    if not summary.assumptions_valid:
        return VerdictDecision(
            Verdict.UNVERIFIED,
            "Assumption evidence validation failed",
        )

    if not summary.semantic_guard_passed:
        return VerdictDecision(
            Verdict.UNVERIFIED,
            "Semantic guard checks failed",
        )

    if summary.all_obligations_passed:
        if summary.repaired:
            return VerdictDecision(
                Verdict.FIXED,
                "All obligations passed after repair",
            )
        return VerdictDecision(Verdict.VERIFIED, "All obligations passed")

    return VerdictDecision(
        Verdict.VULNERABLE,
        "One or more canonical obligations failed",
    )

