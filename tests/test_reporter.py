from src.core.models import AssumedInput, Obligation, Verdict
from src.core.reporter import FileReport, render_json_report, render_markdown_report, render_mr_comment


def _report() -> FileReport:
    return FileReport(
        filename="withdraw.py",
        verdict=Verdict.VERIFIED,
        obligations=[
            Obligation(
                id="withdraw:non_negative_result",
                property="withdraw(...) >= 0",
                category="non_negativity",
                description="non-negative",
            )
        ],
        assumptions=[
            AssumedInput(
                property="amount > 0",
                description="validated amount",
                justification="schema",
                source_type="api_schema",
                source_ref="WithdrawRequest.amount",
                evidence_id="schema-v1",
            )
        ],
        engine="lean",
        message="ok",
    )


def test_render_json_report() -> None:
    payload = render_json_report([_report()])
    assert payload["summary"]["verified"] == 1
    assert payload["files"][0]["filename"] == "withdraw.py"


def test_render_markdown_report_contains_table() -> None:
    report = render_markdown_report([_report()])
    assert "| File | Verdict | Engine |" in report
    assert "withdraw.py" in report


def test_render_mr_comment() -> None:
    text = render_mr_comment([_report()])
    assert "Argus Formal Verification Report" in text
    assert "withdraw.py" in text

