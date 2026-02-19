from src.core.assumption_evidence import validate_assumptions
from src.core.models import AssumedInput


def test_assumption_evidence_passes_with_complete_provenance() -> None:
    assumptions = [
        AssumedInput(
            property="amount > 0",
            description="validated amount",
            justification="API schema enforces minimum",
            source_type="api_schema",
            source_ref="schemas/WithdrawRequest.amount",
            evidence_id="withdraw-schema-v1",
        )
    ]
    ok, issues = validate_assumptions(assumptions)
    assert ok
    assert issues == []


def test_assumption_evidence_fails_when_missing_fields() -> None:
    assumptions = [
        AssumedInput(
            property="amount > 0",
            description="validated amount",
            justification="",
            source_type="api_schema",
            source_ref="",
            evidence_id="",
        )
    ]
    ok, issues = validate_assumptions(assumptions)
    assert not ok
    assert len(issues) == 3


def test_assumption_evidence_fails_for_unsupported_source_type() -> None:
    assumptions = [
        AssumedInput(
            property="balance >= 0",
            description="policy assumption",
            justification="manual note",
            source_type="type_semantics",
            source_ref="n/a",
            evidence_id="n/a",
        )
    ]
    ok, issues = validate_assumptions(assumptions)
    assert not ok
    assert any("Unsupported source_type" in issue.reason for issue in issues)

