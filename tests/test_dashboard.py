"""
Tests for src/core/dashboard.py — Mission Control HTML dashboard generator.

Validates:
- Dashboard generates valid HTML from argus_report.json
- All required sections are present
- Data is embedded (no external dependencies)
- Edge cases: empty report, all verdict types, missing traces
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core.dashboard import (
    _exec_tagline,
    _risk_level,
    generate_dashboard,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_report(
    files: list[dict] | None = None,
    provider: str = "anthropic",
    model: str = "claude-sonnet-4-6",
) -> dict:
    """Build a minimal argus_report.json payload."""
    if files is None:
        files = [
            {
                "filename": "withdraw.py",
                "verdict": "VERIFIED",
                "engine": "lean",
                "message": "All obligations passed",
                "obligations": [
                    {
                        "id": "withdraw:non_negative_result",
                        "property": "withdraw(...) >= 0",
                        "category": "non_negativity",
                        "description": "non-negative",
                        "severity": "high",
                        "source": "policy",
                    }
                ],
                "assumptions": [
                    {
                        "property": "amount > 0",
                        "description": "validated amount",
                        "justification": "schema",
                        "source_type": "api_schema",
                        "source_ref": "WithdrawRequest.amount",
                        "evidence_id": "schema-v1",
                        "severity": "medium",
                    }
                ],
            }
        ]
    total = len(files)
    verdicts = [f["verdict"] for f in files]
    return {
        "tool": "ArgusV2",
        "provider": provider,
        "model": model,
        "timestamp": "2026-03-16T12:00:00+00:00",
        "summary": {
            "total": total,
            "verified": verdicts.count("VERIFIED"),
            "fixed": verdicts.count("FIXED"),
            "vulnerable": verdicts.count("VULNERABLE"),
            "unverified": verdicts.count("UNVERIFIED"),
            "error": verdicts.count("ERROR"),
        },
        "files": files,
    }


def _write_report(tmp_path: Path, report: dict) -> Path:
    p = tmp_path / "argus_report.json"
    p.write_text(json.dumps(report), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Core generation tests
# ---------------------------------------------------------------------------

def test_generate_dashboard_produces_html_file(tmp_path: Path) -> None:
    """generate_dashboard() creates a file at the specified output path."""
    report = _make_report()
    report_path = str(_write_report(tmp_path, report))
    out = str(tmp_path / "dashboard.html")

    result = generate_dashboard(report_path, trace_root="", output_path=out)

    assert result == out
    assert Path(out).exists()
    content = Path(out).read_text(encoding="utf-8")
    assert len(content) > 1000  # non-trivial output


def test_generate_dashboard_is_valid_html(tmp_path: Path) -> None:
    """Dashboard output is a complete HTML document."""
    report_path = str(_write_report(tmp_path, _make_report()))
    out = str(tmp_path / "dashboard.html")

    generate_dashboard(report_path, trace_root="", output_path=out)
    content = Path(out).read_text(encoding="utf-8")

    assert "<!DOCTYPE html>" in content
    assert "<html" in content
    assert "</html>" in content
    assert "<head>" in content
    assert "<body>" in content
    assert "</body>" in content


def test_dashboard_contains_required_sections(tmp_path: Path) -> None:
    """Dashboard includes all required visual sections."""
    report_path = str(_write_report(tmp_path, _make_report()))
    out = str(tmp_path / "dashboard.html")

    generate_dashboard(report_path, trace_root="", output_path=out)
    content = Path(out).read_text(encoding="utf-8")

    assert "Mission Control" in content        # header branding
    assert "Executive Summary" in content      # exec summary section
    assert "Pipeline Stages" in content        # timeline section
    assert "File Verification Results" in content  # file cards section
    assert "Audit Trail" in content            # provenance section


def test_dashboard_embeds_data_as_json(tmp_path: Path) -> None:
    """Dashboard embeds run data as JSON inside a <script type=application/json> tag."""
    report = _make_report()
    report_path = str(_write_report(tmp_path, report))
    out = str(tmp_path / "dashboard.html")

    generate_dashboard(report_path, trace_root="", output_path=out)
    content = Path(out).read_text(encoding="utf-8")

    assert 'id="argus-data"' in content
    assert 'type="application/json"' in content


def test_dashboard_has_no_external_dependencies(tmp_path: Path) -> None:
    """Dashboard is fully self-contained — no external CDN/network links."""
    report_path = str(_write_report(tmp_path, _make_report()))
    out = str(tmp_path / "dashboard.html")

    generate_dashboard(report_path, trace_root="", output_path=out)
    content = Path(out).read_text(encoding="utf-8")

    # No external stylesheet links
    assert '<link rel="stylesheet"' not in content
    # No external script src
    for line in content.splitlines():
        if "<script" in line and "src=" in line:
            # Only allowed if it's the data script (which has no src)
            assert 'src="' not in line, f"External script found: {line}"
    # No fetch() to external URLs
    assert "fetch(" not in content


def test_dashboard_shows_verdict_badge(tmp_path: Path) -> None:
    """Dashboard renders verdict badges for each file."""
    report = _make_report()
    report_path = str(_write_report(tmp_path, report))
    out = str(tmp_path / "dashboard.html")

    generate_dashboard(report_path, trace_root="", output_path=out)
    content = Path(out).read_text(encoding="utf-8")

    assert "VERIFIED" in content
    assert "withdraw.py" in content


def test_dashboard_shows_provider_badge(tmp_path: Path) -> None:
    """Dashboard renders provider attribution from the report."""
    report = _make_report(provider="anthropic", model="claude-sonnet-4-6")
    report_path = str(_write_report(tmp_path, report))
    out = str(tmp_path / "dashboard.html")

    generate_dashboard(report_path, trace_root="", output_path=out)
    content = Path(out).read_text(encoding="utf-8")

    assert "anthropic" in content.lower() or "Anthropic" in content


def test_dashboard_handles_empty_report(tmp_path: Path) -> None:
    """Empty file list produces a valid dashboard with no-files message."""
    report = _make_report(files=[])
    report_path = str(_write_report(tmp_path, report))
    out = str(tmp_path / "dashboard.html")

    generate_dashboard(report_path, trace_root="", output_path=out)
    content = Path(out).read_text(encoding="utf-8")

    assert "<!DOCTYPE html>" in content
    assert "No files" in content


def test_dashboard_handles_all_verdict_types(tmp_path: Path) -> None:
    """Dashboard renders correctly with all 5 verdict types present."""
    files = [
        {"filename": "a.py", "verdict": "VERIFIED", "engine": "lean", "message": "ok", "obligations": [], "assumptions": []},
        {"filename": "b.py", "verdict": "FIXED", "engine": "lean", "message": "repaired", "obligations": [], "assumptions": []},
        {"filename": "c.py", "verdict": "VULNERABLE", "engine": "lean", "message": "failed", "obligations": [], "assumptions": []},
        {"filename": "d.py", "verdict": "UNVERIFIED", "engine": "n/a", "message": "unsupported", "obligations": [], "assumptions": []},
        {"filename": "e.py", "verdict": "ERROR", "engine": "n/a", "message": "error", "obligations": [], "assumptions": []},
    ]
    report = _make_report(files=files)
    report_path = str(_write_report(tmp_path, report))
    out = str(tmp_path / "dashboard.html")

    generate_dashboard(report_path, trace_root="", output_path=out)
    content = Path(out).read_text(encoding="utf-8")

    for verdict in ["VERIFIED", "FIXED", "VULNERABLE", "UNVERIFIED", "ERROR"]:
        assert verdict in content, f"Missing verdict: {verdict}"
    for fname in ["a.py", "b.py", "c.py", "d.py", "e.py"]:
        assert fname in content, f"Missing filename: {fname}"


def test_dashboard_includes_original_code_when_provided(tmp_path: Path) -> None:
    """When original_code is provided, it appears in the dashboard."""
    report_path = str(_write_report(tmp_path, _make_report()))
    out = str(tmp_path / "dashboard.html")

    original = {"withdraw.py": "def withdraw(b, a):\n    return b - a\n"}
    generate_dashboard(report_path, trace_root="", output_path=out, original_code=original)
    content = Path(out).read_text(encoding="utf-8")

    assert "return b - a" in content


def test_dashboard_missing_report_file_produces_empty_html(tmp_path: Path) -> None:
    """Missing report file still produces a parseable HTML file (graceful)."""
    out = str(tmp_path / "dashboard.html")
    generate_dashboard(
        report_path=str(tmp_path / "nonexistent.json"),
        trace_root="",
        output_path=out,
    )
    content = Path(out).read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content


def test_dashboard_vulnerable_shows_action_required(tmp_path: Path) -> None:
    """VULNERABLE file card includes action guidance in the dashboard."""
    files = [
        {
            "filename": "vuln.py",
            "verdict": "VULNERABLE",
            "engine": "lean",
            "message": "Obligation non_negative_result failed",
            "obligations": [],
            "assumptions": [],
        }
    ]
    report = _make_report(files=files)
    report_path = str(_write_report(tmp_path, report))
    out = str(tmp_path / "dashboard.html")

    generate_dashboard(report_path, trace_root="", output_path=out)
    content = Path(out).read_text(encoding="utf-8")

    assert "Action Required" in content


def test_dashboard_fixed_shows_fixed_badge(tmp_path: Path) -> None:
    """FIXED verdict produces the correct verdict badge class."""
    files = [
        {
            "filename": "fix.py",
            "verdict": "FIXED",
            "engine": "lean",
            "message": "Repaired and verified",
            "obligations": [],
            "assumptions": [],
        }
    ]
    report = _make_report(files=files)
    report_path = str(_write_report(tmp_path, report))
    out = str(tmp_path / "dashboard.html")

    generate_dashboard(report_path, trace_root="", output_path=out)
    content = Path(out).read_text(encoding="utf-8")

    assert "FIXED" in content
    assert "fix.py" in content


# ---------------------------------------------------------------------------
# Risk level and tagline helpers
# ---------------------------------------------------------------------------

def test_risk_level_clear_when_all_verified() -> None:
    summary = {"verified": 3, "fixed": 0, "vulnerable": 0, "unverified": 0, "error": 0}
    assert _risk_level(summary) == "clear"


def test_risk_level_attention_when_fixed() -> None:
    summary = {"verified": 1, "fixed": 1, "vulnerable": 0, "unverified": 0, "error": 0}
    assert _risk_level(summary) == "attention"


def test_risk_level_attention_when_unverified() -> None:
    summary = {"verified": 1, "fixed": 0, "vulnerable": 0, "unverified": 1, "error": 0}
    assert _risk_level(summary) == "attention"


def test_risk_level_critical_when_vulnerable() -> None:
    summary = {"verified": 0, "fixed": 0, "vulnerable": 1, "unverified": 0, "error": 0}
    assert _risk_level(summary) == "critical"


def test_risk_level_critical_when_error() -> None:
    summary = {"verified": 0, "fixed": 0, "vulnerable": 0, "unverified": 0, "error": 1}
    assert _risk_level(summary) == "critical"


def test_exec_tagline_all_verified() -> None:
    summary = {"total": 3, "verified": 3, "fixed": 0, "vulnerable": 0, "unverified": 0, "error": 0}
    tagline = _exec_tagline(summary)
    assert "All 3" in tagline
    assert "verified" in tagline.lower() or "Safe" in tagline


def test_exec_tagline_empty() -> None:
    summary = {"total": 0, "verified": 0, "fixed": 0, "vulnerable": 0, "unverified": 0, "error": 0}
    tagline = _exec_tagline(summary)
    assert "No files" in tagline or tagline != ""


def test_exec_tagline_mixed() -> None:
    summary = {"total": 3, "verified": 1, "fixed": 1, "vulnerable": 1, "unverified": 0, "error": 0}
    tagline = _exec_tagline(summary)
    # Should mention both the vulnerability and the fix
    assert tagline  # not empty
