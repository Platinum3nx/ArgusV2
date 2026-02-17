from src.core.models import AssumedInput, Verdict
from src.core.quality_gates import assumption_coverage_gate, unsupported_fail_closed_gate


def test_assumption_coverage_gate_passes() -> None:
    assumptions = [
        AssumedInput(
            property="amount > 0",
            description="validated",
            justification="api schema",
            source_type="api_schema",
            source_ref="WithdrawRequest.amount",
            evidence_id="schema-v1",
        )
    ]
    result = assumption_coverage_gate(assumptions)
    assert result.passed


def test_unsupported_fail_closed_gate_requires_unverified_verdict() -> None:
    result = unsupported_fail_closed_gate(Verdict.UNVERIFIED, ["async_function"])
    assert result.passed

    failing = unsupported_fail_closed_gate(Verdict.VERIFIED, ["async_function"])
    assert not failing.passed

