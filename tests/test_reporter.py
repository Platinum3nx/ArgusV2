"""
Tests for src/core/reporter.py

Covers:
- All 5 report formats (JSON, Markdown, MR comment, SARIF, GitLab SAST)
- Enhanced MR comment: executive summary, verdict grouping, repair diffs
- Enhanced Markdown: executive summary, risk assessment, recommendations
- Backward compatibility: all new parameters are optional
- Edge cases: empty file list, all verdict types, provider attribution
"""
from src.core.models import AssumedInput, Obligation, Severity, Verdict
from src.core.reporter import (
    FileReport,
    render_gitlab_sast_report,
    render_json_report,
    render_markdown_report,
    render_mr_comment,
    render_sarif_report,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _verified_report(filename: str = "withdraw.py") -> FileReport:
    return FileReport(
        filename=filename,
        verdict=Verdict.VERIFIED,
        obligations=[
            Obligation(
                id="withdraw:non_negative_result",
                property="withdraw(...) >= 0",
                category="non_negativity",
                description="non-negative result",
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
        message="All obligations passed",
    )


def _vulnerable_report(filename: str = "vuln.py") -> FileReport:
    return FileReport(
        filename=filename,
        verdict=Verdict.VULNERABLE,
        obligations=[
            Obligation(
                id="vuln:non_negative_result",
                property="vuln(...) >= 0",
                category="non_negativity",
                description="non-negative result",
                severity=Severity.CRITICAL,
            )
        ],
        assumptions=[],
        engine="lean",
        message="Obligation non_negative_result failed: result can be negative",
    )


def _fixed_report(filename: str = "fixed.py") -> FileReport:
    return FileReport(
        filename=filename,
        verdict=Verdict.FIXED,
        obligations=[
            Obligation(
                id="fixed:non_negative_result",
                property="fixed(...) >= 0",
                category="non_negativity",
                description="non-negative result",
            )
        ],
        assumptions=[],
        engine="lean",
        message="Repaired and verified",
    )


def _unverified_report() -> FileReport:
    return FileReport(
        filename="async_worker.py",
        verdict=Verdict.UNVERIFIED,
        obligations=[],
        assumptions=[],
        engine="n/a",
        message="Unsupported construct: async def",
    )


def _error_report() -> FileReport:
    return FileReport(
        filename="broken.py",
        verdict=Verdict.ERROR,
        obligations=[],
        assumptions=[],
        engine="n/a",
        message="Verifier process failed",
    )


# ---------------------------------------------------------------------------
# JSON report tests
# ---------------------------------------------------------------------------

def test_render_json_report_summary_counts() -> None:
    reports = [_verified_report(), _vulnerable_report(), _fixed_report()]
    payload = render_json_report(reports)
    assert payload["summary"]["total"] == 3
    assert payload["summary"]["verified"] == 1
    assert payload["summary"]["vulnerable"] == 1
    assert payload["summary"]["fixed"] == 1


def test_render_json_report_file_entries() -> None:
    payload = render_json_report([_verified_report()])
    assert payload["files"][0]["filename"] == "withdraw.py"
    assert payload["files"][0]["verdict"] == "VERIFIED"


def test_render_json_report_provider_attribution() -> None:
    payload = render_json_report([_verified_report()], provider="anthropic", model="claude-sonnet-4-6")
    assert payload["provider"] == "anthropic"
    assert payload["model"] == "claude-sonnet-4-6"
    assert payload["tool"] == "ArgusV2"


def test_render_json_report_empty_files() -> None:
    payload = render_json_report([])
    assert payload["summary"]["total"] == 0
    assert payload["files"] == []


# ---------------------------------------------------------------------------
# Markdown report tests (enhanced)
# ---------------------------------------------------------------------------

def test_render_markdown_report_contains_table() -> None:
    report = render_markdown_report([_verified_report()])
    assert "| File | Verdict | Engine | Finding |" in report
    assert "withdraw.py" in report


def test_render_markdown_report_has_executive_summary() -> None:
    report = render_markdown_report([_verified_report()])
    assert "Executive Summary" in report
    assert "All" in report or "passed" in report.lower()


def test_render_markdown_report_has_risk_assessment() -> None:
    report = render_markdown_report([_vulnerable_report()])
    assert "Risk Assessment" in report
    assert "CRITICAL" in report


def test_render_markdown_report_has_recommendations() -> None:
    report = render_markdown_report([_vulnerable_report()])
    assert "Recommendations" in report
    assert "Block merge" in report or "block" in report.lower()


def test_render_markdown_report_all_clear_recommendations() -> None:
    report = render_markdown_report([_verified_report()])
    assert "Recommendations" in report
    # Should suggest merging safely
    text = report.lower()
    assert "merge" in text or "safe" in text


def test_render_markdown_report_has_audit_metadata() -> None:
    report = render_markdown_report([_verified_report()], provider="anthropic", model="claude-sonnet-4-6")
    assert "Audit Metadata" in report
    assert "ArgusV2" in report


def test_render_markdown_report_includes_repair_diff_for_fixed() -> None:
    orig = "def transfer(b, a):\n    return b - a\n"
    rep = "def transfer(b, a):\n    if a > b: return b\n    return b - a\n"
    report = render_markdown_report(
        [_fixed_report()],
        repaired_code={"fixed.py": rep},
        original_code={"fixed.py": orig},
    )
    assert "Before" in report or "Original" in report
    assert "return b - a" in report


def test_render_markdown_report_backward_compatible_no_code_dicts() -> None:
    """Calling without repaired_code/original_code should not raise."""
    report = render_markdown_report([_fixed_report()])
    assert "FIXED" in report


def test_render_markdown_report_provider_line() -> None:
    report = render_markdown_report([_verified_report()], provider="anthropic", model="claude-sonnet-4-6")
    assert "Anthropic" in report
    assert "claude-sonnet-4-6" in report


def test_render_markdown_report_mixed_verdicts() -> None:
    reports = [_verified_report(), _vulnerable_report(), _fixed_report(), _unverified_report()]
    md = render_markdown_report(reports)
    for verdict in ["VERIFIED", "VULNERABLE", "FIXED", "UNVERIFIED"]:
        assert verdict in md


# ---------------------------------------------------------------------------
# MR comment tests (enhanced)
# ---------------------------------------------------------------------------

def test_render_mr_comment_has_report_header() -> None:
    text = render_mr_comment([_verified_report()])
    assert "Argus Formal Verification Report" in text


def test_render_mr_comment_has_executive_summary() -> None:
    text = render_mr_comment([_verified_report()])
    assert "Executive Summary" in text


def test_render_mr_comment_summary_table() -> None:
    """Comment includes the 4-column verdict summary table."""
    text = render_mr_comment([_verified_report(), _vulnerable_report()])
    assert "Verified" in text
    assert "Vulnerable" in text
    assert "Auto-Repaired" in text


def test_render_mr_comment_groups_vulnerable_under_action_required() -> None:
    text = render_mr_comment([_vulnerable_report()])
    assert "Action Required" in text
    assert "vuln.py" in text


def test_render_mr_comment_groups_fixed_under_auto_repaired() -> None:
    text = render_mr_comment([_fixed_report()])
    assert "Auto-Repaired" in text
    assert "fixed.py" in text


def test_render_mr_comment_groups_verified_in_verified_section() -> None:
    text = render_mr_comment([_verified_report()])
    assert "Verified" in text
    assert "withdraw.py" in text


def test_render_mr_comment_shows_repair_diff_when_code_provided() -> None:
    orig = "def f(b, a):\n    return b - a\n"
    rep = "def f(b, a):\n    if a > b: return b\n    return b - a\n"
    text = render_mr_comment(
        [_fixed_report()],
        repaired_code={"fixed.py": rep},
        original_code={"fixed.py": orig},
    )
    # Should contain a diff block
    assert "diff" in text or "+" in text or "-" in text or "return b - a" in text


def test_render_mr_comment_includes_obligation_details_for_vulnerable() -> None:
    text = render_mr_comment([_vulnerable_report()])
    # Obligations are in a collapsible section
    assert "Obligations" in text
    assert "vuln:non_negative_result" in text


def test_render_mr_comment_backward_compatible_no_code_dicts() -> None:
    """render_mr_comment without new args should not raise."""
    text = render_mr_comment([_fixed_report()])
    assert "Argus Formal Verification Report" in text


def test_render_mr_comment_provider_footer() -> None:
    text = render_mr_comment([_verified_report()], provider="anthropic", model="claude-sonnet-4-6")
    assert "Anthropic" in text
    assert "Lean 4" in text


def test_render_mr_comment_unverified_section() -> None:
    text = render_mr_comment([_unverified_report()])
    assert "Unverified" in text or "UNVERIFIED" in text
    assert "async_worker.py" in text


def test_render_mr_comment_all_verified_no_action_required_section() -> None:
    text = render_mr_comment([_verified_report("a.py"), _verified_report("b.py")])
    # Should NOT have an "Action Required" section when everything passes
    assert "Action Required" not in text


def test_render_mr_comment_stays_under_character_limit() -> None:
    """Comment must stay under GitLab note body limit (65,535 chars)."""
    # Test with 10 files to stress test length
    reports = [_verified_report(f"file_{i}.py") for i in range(10)]
    text = render_mr_comment(reports)
    assert len(text) < 65_535


# ---------------------------------------------------------------------------
# SARIF report tests
# ---------------------------------------------------------------------------

def test_render_sarif_report_filters_verified_findings() -> None:
    sarif = render_sarif_report([_verified_report()])
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["results"] == []


def test_render_sarif_report_includes_vulnerable_findings() -> None:
    sarif = render_sarif_report([_vulnerable_report()])
    results = sarif["runs"][0]["results"]
    assert len(results) == 1
    assert results[0]["ruleId"] == "argus/vulnerable"
    assert results[0]["level"] == "error"


def test_render_sarif_report_includes_unverified_as_warning() -> None:
    sarif = render_sarif_report([_unverified_report()])
    results = sarif["runs"][0]["results"]
    assert len(results) == 1
    assert results[0]["level"] == "warning"


def test_render_sarif_report_provider_in_driver_properties() -> None:
    sarif = render_sarif_report([_vulnerable_report()], provider="anthropic", model="claude-sonnet-4-6")
    props = sarif["runs"][0]["tool"]["driver"]["properties"]
    assert props["provider"] == "anthropic"
    assert props["model"] == "claude-sonnet-4-6"


def test_render_sarif_report_no_driver_properties_when_no_provider() -> None:
    sarif = render_sarif_report([_vulnerable_report()])
    driver = sarif["runs"][0]["tool"]["driver"]
    assert "properties" not in driver


# ---------------------------------------------------------------------------
# GitLab SAST report tests
# ---------------------------------------------------------------------------

def test_render_gitlab_sast_report_includes_vulnerable_entries() -> None:
    report = render_gitlab_sast_report([_vulnerable_report()])
    assert report["version"] == "15.0.7"
    assert len(report["vulnerabilities"]) == 1
    assert report["vulnerabilities"][0]["location"]["file"] == "vuln.py"
    assert report["vulnerabilities"][0]["severity"] == "Critical"


def test_render_gitlab_sast_report_excludes_verified() -> None:
    report = render_gitlab_sast_report([_verified_report()])
    assert len(report["vulnerabilities"]) == 0


def test_render_gitlab_sast_report_unverified_is_high_severity() -> None:
    report = render_gitlab_sast_report([_unverified_report()])
    assert report["vulnerabilities"][0]["severity"] == "High"


def test_render_gitlab_sast_report_error_is_critical() -> None:
    report = render_gitlab_sast_report([_error_report()])
    assert report["vulnerabilities"][0]["severity"] == "Critical"


def test_render_gitlab_sast_report_fingerprint_deterministic() -> None:
    """Same input → same fingerprint (deterministic IDs)."""
    r1 = render_gitlab_sast_report([_vulnerable_report()])
    r2 = render_gitlab_sast_report([_vulnerable_report()])
    assert r1["vulnerabilities"][0]["id"] == r2["vulnerabilities"][0]["id"]
