from src.core.models import Obligation, ObligationResult, VerificationSummary, Verdict
from src.core.verdict import compute_verdict


def _obligation_result(ok: bool) -> ObligationResult:
    obligation = Obligation(
        id="f:non_negative_result",
        property="f(...) >= 0",
        category="non_negativity",
        description="non-negative",
    )
    return ObligationResult(obligation=obligation, verified=ok, engine="lean")


def test_verdict_verified_when_all_pass() -> None:
    summary = VerificationSummary(
        obligation_results=[_obligation_result(True)],
        assumptions_valid=True,
        unsupported_constructs=[],
        semantic_guard_passed=True,
        repaired=False,
    )
    decision = compute_verdict(summary)
    assert decision.verdict == Verdict.VERIFIED


def test_verdict_fixed_when_repaired_and_all_pass() -> None:
    summary = VerificationSummary(
        obligation_results=[_obligation_result(True)],
        assumptions_valid=True,
        unsupported_constructs=[],
        semantic_guard_passed=True,
        repaired=True,
    )
    decision = compute_verdict(summary)
    assert decision.verdict == Verdict.FIXED


def test_verdict_unverified_when_assumptions_invalid() -> None:
    summary = VerificationSummary(
        obligation_results=[_obligation_result(True)],
        assumptions_valid=False,
        unsupported_constructs=[],
        semantic_guard_passed=True,
    )
    decision = compute_verdict(summary)
    assert decision.verdict == Verdict.UNVERIFIED


def test_verdict_unverified_when_unsupported_construct_present() -> None:
    summary = VerificationSummary(
        obligation_results=[_obligation_result(True)],
        assumptions_valid=True,
        unsupported_constructs=["async_function"],
        semantic_guard_passed=True,
    )
    decision = compute_verdict(summary)
    assert decision.verdict == Verdict.UNVERIFIED


def test_verdict_vulnerable_when_obligation_fails() -> None:
    summary = VerificationSummary(
        obligation_results=[_obligation_result(False)],
        assumptions_valid=True,
        unsupported_constructs=[],
        semantic_guard_passed=True,
    )
    decision = compute_verdict(summary)
    assert decision.verdict == Verdict.VULNERABLE


def test_verdict_error_on_verification_error() -> None:
    summary = VerificationSummary(
        obligation_results=[_obligation_result(True)],
        assumptions_valid=True,
        unsupported_constructs=[],
        semantic_guard_passed=True,
        verification_error=True,
    )
    decision = compute_verdict(summary)
    assert decision.verdict == Verdict.ERROR

