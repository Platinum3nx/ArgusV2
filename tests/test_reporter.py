from src.core.models import AssumedInput, Obligation, Verdict
from src.core.reporter import (
    FileReport,
    render_gitlab_sast_report,
    render_json_report,
    render_markdown_report,
    render_mr_comment,
    render_sarif_report,
)


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


def test_render_sarif_report_filters_verified_findings() -> None:
    sarif = render_sarif_report([_report()])
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["results"] == []


def test_render_gitlab_sast_report_includes_vulnerable_entries() -> None:
    vulnerable = FileReport(
        filename="auth.py",
        verdict=Verdict.VULNERABLE,
        obligations=[],
        assumptions=[],
        engine="lean",
        message="State transition can bypass authorization checks",
    )
    report = render_gitlab_sast_report([vulnerable])
    assert report["version"] == "15.0.7"
    assert len(report["vulnerabilities"]) == 1
    assert report["vulnerabilities"][0]["location"]["file"] == "auth.py"
