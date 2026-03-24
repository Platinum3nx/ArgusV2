"""
ArgusV2 Mission Control — Self-contained HTML dashboard generator.

Reads pipeline artifacts (argus_report.json + .argus-trace/) and produces
a single argus_dashboard.html file that opens in any modern browser with no
external dependencies. Designed for judge comprehension within 45 seconds.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# CSS + JS template (all inline, no external deps)
# ---------------------------------------------------------------------------

_CSS = """
:root {
  --bg: #0d1117;
  --bg2: #161b22;
  --bg3: #21262d;
  --border: #30363d;
  --text: #e6edf3;
  --text-muted: #8b949e;
  --verified: #3fb950;
  --verified-bg: #0f2d1a;
  --fixed: #d29922;
  --fixed-bg: #2d1f00;
  --vulnerable: #f85149;
  --vulnerable-bg: #2d0f0f;
  --unverified: #f0883e;
  --unverified-bg: #2d1800;
  --error: #6e7681;
  --error-bg: #1c1e20;
  --accent: #58a6ff;
  --anthropic: #d97757;
  --lean: #7c3aed;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
  font-size: 14px;
  line-height: 1.6;
}

a { color: var(--accent); text-decoration: none; }

/* Header */
.header {
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  padding: 16px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-logo {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent), var(--lean));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}
.header-title { font-size: 18px; font-weight: 700; }
.header-subtitle { font-size: 12px; color: var(--text-muted); }
.header-meta {
  display: flex;
  gap: 16px;
  align-items: center;
  font-size: 12px;
  color: var(--text-muted);
}
.provider-badge {
  background: #2a1e12;
  border: 1px solid var(--anthropic);
  color: var(--anthropic);
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}
.run-id { font-family: monospace; color: var(--text-muted); }

/* Layout */
.container { max-width: 1200px; margin: 0 auto; padding: 24px 32px; }

/* Executive Summary */
.exec-summary {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}
.exec-summary h2 { font-size: 16px; font-weight: 700; margin-bottom: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.exec-tagline { font-size: 20px; font-weight: 600; margin-bottom: 16px; }
.exec-tagline.clear { color: var(--verified); }
.exec-tagline.attention { color: var(--fixed); }
.exec-tagline.critical { color: var(--vulnerable); }
.verdict-counts {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.count-card {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 20px;
  text-align: center;
  min-width: 100px;
}
.count-card .number { font-size: 28px; font-weight: 700; font-family: monospace; }
.count-card .label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); }
.count-card.verified .number { color: var(--verified); }
.count-card.fixed .number { color: var(--fixed); }
.count-card.vulnerable .number { color: var(--vulnerable); }
.count-card.unverified .number { color: var(--unverified); }
.count-card.error .number { color: var(--error); }
.risk-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  margin-top: 16px;
}
.risk-badge.clear { background: var(--verified-bg); color: var(--verified); border: 1px solid var(--verified); }
.risk-badge.attention { background: var(--fixed-bg); color: var(--fixed); border: 1px solid var(--fixed); }
.risk-badge.critical { background: var(--vulnerable-bg); color: var(--vulnerable); border: 1px solid var(--vulnerable); }

/* Pipeline Timeline */
.timeline {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}
.timeline h2 { font-size: 16px; font-weight: 700; margin-bottom: 20px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.timeline-stages {
  display: flex;
  align-items: center;
  gap: 0;
  flex-wrap: wrap;
  row-gap: 12px;
}
.stage {
  display: flex;
  align-items: center;
  gap: 0;
}
.stage-box {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 16px;
  text-align: center;
  min-width: 100px;
  transition: border-color 0.2s;
}
.stage-box.active { border-color: var(--verified); }
.stage-box.skipped { opacity: 0.4; }
.stage-icon { font-size: 18px; margin-bottom: 4px; }
.stage-name { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.stage-desc { font-size: 10px; color: var(--text-muted); margin-top: 2px; }
.stage-arrow { color: var(--border); font-size: 20px; padding: 0 6px; }

/* File Cards */
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
  margin-top: 8px;
}
.file-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
  transition: border-color 0.2s;
}
.file-card:hover { border-color: #444c56; }
.file-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;
}
.file-header:hover { background: var(--bg3); }
.file-info { display: flex; align-items: center; gap: 12px; }
.file-icon { font-size: 20px; }
.file-name { font-family: monospace; font-size: 15px; font-weight: 600; }
.file-engine { font-size: 11px; color: var(--text-muted); }
.file-right { display: flex; align-items: center; gap: 12px; }
.verdict-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.verdict-badge.VERIFIED { background: var(--verified-bg); color: var(--verified); border: 1px solid var(--verified); }
.verdict-badge.FIXED { background: var(--fixed-bg); color: var(--fixed); border: 1px solid var(--fixed); }
.verdict-badge.VULNERABLE { background: var(--vulnerable-bg); color: var(--vulnerable); border: 1px solid var(--vulnerable); }
.verdict-badge.UNVERIFIED { background: var(--unverified-bg); color: var(--unverified); border: 1px solid var(--unverified); }
.verdict-badge.ERROR { background: var(--error-bg); color: var(--error); border: 1px solid var(--error); }
.chevron { font-size: 14px; color: var(--text-muted); transition: transform 0.2s; }
.chevron.open { transform: rotate(180deg); }

.file-body { border-top: 1px solid var(--border); display: none; }
.file-body.open { display: block; }
.file-section { padding: 20px; border-bottom: 1px solid var(--border); }
.file-section:last-child { border-bottom: none; }
.file-section-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 12px; }

/* Obligation table */
.obligation-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.obligation-table th { text-align: left; padding: 8px 12px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); border-bottom: 1px solid var(--border); }
.obligation-table td { padding: 10px 12px; border-bottom: 1px solid var(--border); }
.obligation-table tr:last-child td { border-bottom: none; }
.obl-pass { color: var(--verified); font-weight: 700; }
.obl-fail { color: var(--vulnerable); font-weight: 700; }
.obl-unknown { color: var(--unverified); font-weight: 700; }
.obl-id { font-family: monospace; font-size: 12px; }
.severity-critical { color: var(--vulnerable); }
.severity-high { color: var(--unverified); }
.severity-medium { color: var(--fixed); }
.severity-low { color: var(--text-muted); }

/* Message box */
.message-box {
  background: var(--bg3);
  border-radius: 8px;
  padding: 12px 16px;
  font-family: monospace;
  font-size: 13px;
  color: var(--text-muted);
  border-left: 3px solid var(--border);
}
.message-box.vulnerable { border-left-color: var(--vulnerable); color: #f8a5a2; }
.message-box.verified { border-left-color: var(--verified); color: #7ee787; }
.message-box.fixed { border-left-color: var(--fixed); color: #e3b341; }

/* Action items */
.action-box {
  background: var(--vulnerable-bg);
  border: 1px solid var(--vulnerable);
  border-radius: 8px;
  padding: 14px 16px;
}
.action-box p { margin-top: 6px; font-size: 13px; color: #f8a5a2; }
.action-title { font-size: 13px; font-weight: 700; color: var(--vulnerable); }

/* Code panels */
.code-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.code-panel { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.code-panel-header { padding: 8px 14px; background: var(--bg3); border-bottom: 1px solid var(--border); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; display: flex; align-items: center; gap: 8px; }
.code-panel-header .lang-badge { background: var(--lean); color: white; border-radius: 4px; padding: 1px 6px; font-size: 10px; }
.code-panel-header .lang-badge.py { background: #306998; }
.code-panel-header .lang-badge.fixed { background: var(--verified); color: #0d1117; }
.code-body { padding: 14px; overflow-x: auto; font-family: "SFMono-Regular", Consolas, monospace; font-size: 12px; line-height: 1.7; white-space: pre; max-height: 300px; overflow-y: auto; }
.code-body .kw { color: #ff79c6; }
.code-body .fn { color: #50fa7b; }
.code-body .str { color: #f1fa8c; }
.code-body .num { color: #bd93f9; }
.code-body .comment { color: #6272a4; font-style: italic; }
.code-body .op { color: #ff79c6; }

/* Diff */
.diff-line-add { background: #0f2d1a; color: var(--verified); }
.diff-line-remove { background: #2d0f0f; color: var(--vulnerable); }

/* Assumptions */
.assumption-list { list-style: none; }
.assumption-item { padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 13px; display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
.assumption-item:last-child { border-bottom: none; }
.assumption-prop { font-family: monospace; color: var(--accent); }
.assumption-meta { font-size: 11px; color: var(--text-muted); text-align: right; white-space: nowrap; }

/* Audit trail */
.audit-trail {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  margin-top: 24px;
}
.audit-trail h2 { font-size: 16px; font-weight: 700; margin-bottom: 16px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.audit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.audit-item { background: var(--bg3); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; }
.audit-item-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); margin-bottom: 4px; }
.audit-item-value { font-family: monospace; font-size: 13px; word-break: break-all; }

/* Footer */
.footer {
  margin-top: 48px;
  padding: 24px 32px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-muted);
  font-size: 12px;
}
.footer-brand { font-weight: 600; color: var(--text); }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* Responsive */
@media (max-width: 768px) {
  .code-grid { grid-template-columns: 1fr; }
  .audit-grid { grid-template-columns: 1fr; }
  .container { padding: 16px; }
  .timeline-stages { flex-direction: column; align-items: flex-start; }
  .stage-arrow { transform: rotate(90deg); }
}
"""

_JS = """
function toggleCard(el) {
  var card = el.closest('.file-card');
  var body = card.querySelector('.file-body');
  var chevron = card.querySelector('.chevron');
  var isOpen = body.classList.contains('open');
  body.classList.toggle('open', !isOpen);
  chevron.classList.toggle('open', !isOpen);
}

function initDashboard(data) {
  // Nothing needs to be done at init — all rendering is server-side HTML.
  // This function is available for future progressive enhancement.
  console.log('[ArgusV2 Dashboard] Loaded. Run ID:', data.run_id || 'n/a');
}

document.addEventListener('DOMContentLoaded', function() {
  var dataEl = document.getElementById('argus-data');
  if (dataEl) {
    try { initDashboard(JSON.parse(dataEl.textContent)); }
    catch(e) { console.warn('ArgusV2: could not parse embedded data', e); }
  }
});
"""


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _verdict_icon(verdict: str) -> str:
    return {
        "VERIFIED": "✅",
        "FIXED": "🔧",
        "VULNERABLE": "🔴",
        "UNVERIFIED": "⚠️",
        "ERROR": "💀",
    }.get(verdict, "❓")


def _verdict_file_icon(verdict: str) -> str:
    return {
        "VERIFIED": "🛡️",
        "FIXED": "🔧",
        "VULNERABLE": "🚨",
        "UNVERIFIED": "⚠️",
        "ERROR": "💥",
    }.get(verdict, "📄")


def _risk_level(summary: Dict[str, Any]) -> str:
    """Compute aggregate risk level from verdict summary."""
    if summary.get("vulnerable", 0) > 0 or summary.get("error", 0) > 0:
        return "critical"
    if summary.get("unverified", 0) > 0 or summary.get("fixed", 0) > 0:
        return "attention"
    return "clear"


def _risk_label(level: str) -> str:
    return {"critical": "CRITICAL RISK", "attention": "ATTENTION REQUIRED", "clear": "CLEAR"}.get(level, "UNKNOWN")


def _exec_tagline(summary: Dict[str, Any]) -> str:
    total = summary.get("total", 0)
    verified = summary.get("verified", 0)
    fixed = summary.get("fixed", 0)
    vulnerable = summary.get("vulnerable", 0)
    unverified = summary.get("unverified", 0)
    error = summary.get("error", 0)

    if total == 0:
        return "No files were audited in this run."

    parts = []
    if verified == total:
        return f"All {total} file{'s' if total != 1 else ''} passed formal verification. Safe to merge."
    if vulnerable > 0 and fixed == 0:
        parts.append(f"{vulnerable} vulnerability{'s' if vulnerable != 1 else ''} detected")
    if fixed > 0:
        parts.append(f"{fixed} vulnerability{'s' if fixed != 1 else ''} automatically repaired and re-verified")
    if verified > 0:
        parts.append(f"{verified} file{'s' if verified != 1 else ''} verified safe")
    if unverified > 0:
        parts.append(f"{unverified} file{'s' if unverified != 1 else ''} unverified (manual review required)")
    if error > 0:
        parts.append(f"{error} error{'s' if error != 1 else ''} encountered")
    return ". ".join(parts).capitalize() + "." if parts else f"Audited {total} files."


def _html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
    )


def _action_guidance(verdict: str, message: str, obligations: List[Dict]) -> str:
    """Generate actionable developer guidance for non-VERIFIED verdicts."""
    failed = [o for o in obligations if not o.get("verified", False)]
    if verdict == "VULNERABLE":
        failing_ids = ", ".join(o["obligation"]["id"] for o in failed if "obligation" in o)
        guide = f"<div class='action-box'>"
        guide += f"<div class='action-title'>Action Required</div>"
        guide += f"<p><strong>What failed:</strong> {_html_escape(message or 'One or more obligations could not be proven.')}</p>"
        if failing_ids:
            guide += f"<p><strong>Failing obligations:</strong> <code>{_html_escape(failing_ids)}</code></p>"
        guide += f"<p><strong>What to do:</strong> Review the failing obligation(s) above. Add the missing invariant or bounds check to the function, then re-push to trigger re-verification.</p>"
        guide += "</div>"
        return guide
    if verdict == "FIXED":
        return "<div class='message-box fixed'>Argus detected a vulnerability and generated a verified repair. Review the repaired code below before merging.</div>"
    if verdict == "UNVERIFIED":
        return "<div class='message-box'>Argus could not verify this file due to unsupported constructs. Manual security review is recommended.</div>"
    if verdict == "ERROR":
        return "<div class='message-box'>A tooling error occurred. Check the CI logs and re-run. If the error persists, contact your DevSecOps team.</div>"
    return ""


def _render_code_panel(label: str, code: str, lang: str, extra_class: str = "") -> str:
    lang_label = "LEAN 4" if lang == "lean" else "PYTHON"
    badge_class = "py" if lang == "python" else ("fixed" if extra_class == "fixed" else "")
    escaped = _html_escape(code)
    return (
        f"<div class='code-panel'>"
        f"<div class='code-panel-header'>"
        f"<span class='lang-badge {badge_class}'>{lang_label}</span>"
        f" {_html_escape(label)}"
        f"</div>"
        f"<div class='code-body'>{escaped}</div>"
        f"</div>"
    )


def _render_diff(original: str, repaired: str) -> str:
    """Sequential line-by-line diff rendering using difflib."""
    import difflib
    orig_lines = original.splitlines(keepends=True)
    rep_lines = repaired.splitlines(keepends=True)
    diff = difflib.unified_diff(orig_lines, rep_lines, lineterm="")

    html = ["<div class='code-body' style='white-space:pre;'>"]
    for line in diff:
        stripped = line.rstrip("\n")
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            continue
        if line.startswith("-"):
            html.append(f"<div class='diff-line-remove'>{_html_escape(stripped)}</div>")
        elif line.startswith("+"):
            html.append(f"<div class='diff-line-add'>{_html_escape(stripped)}</div>")
        else:
            html.append(f"<div> {_html_escape(stripped)}</div>")
    html.append("</div>")
    return "".join(html)


def _render_obligation_table(obligations: List[Dict], obligation_results: Optional[List[Dict]] = None) -> str:
    """Render obligations with pass/fail status."""
    if not obligations:
        return "<p style='color:var(--text-muted);font-size:13px;'>No obligations recorded.</p>"

    # Build a result lookup by obligation id if results are available
    result_map: Dict[str, bool] = {}
    if obligation_results:
        for r in obligation_results:
            obl = r.get("obligation", {})
            result_map[obl.get("id", "")] = r.get("verified", True)

    rows = []
    for obl in obligations:
        obl_id = obl.get("id", "")
        verified = result_map.get(obl_id, None)
        if verified is None:
            status_html = "<span class='obl-unknown'>UNKNOWN</span>"
        elif verified:
            status_html = "<span class='obl-pass'>PASS</span>"
        else:
            status_html = "<span class='obl-fail'>FAIL</span>"
        sev = obl.get("severity", "high")
        sev_class = f"severity-{sev}"
        rows.append(
            f"<tr>"
            f"<td>{status_html}</td>"
            f"<td><code class='obl-id'>{_html_escape(obl_id)}</code></td>"
            f"<td>{_html_escape(obl.get('property', ''))}</td>"
            f"<td class='{sev_class}'>{sev.upper()}</td>"
            f"<td style='color:var(--text-muted);font-size:12px;'>{_html_escape(obl.get('description', ''))}</td>"
            f"</tr>"
        )

    return (
        f"<table class='obligation-table'>"
        f"<thead><tr><th>Status</th><th>ID</th><th>Property</th><th>Severity</th><th>Description</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        f"</table>"
    )


def _render_assumptions_list(assumptions: List[Dict]) -> str:
    if not assumptions:
        return "<p style='color:var(--text-muted);font-size:13px;'>No explicit assumptions recorded.</p>"
    items = []
    for a in assumptions:
        items.append(
            f"<li class='assumption-item'>"
            f"<span class='assumption-prop'>{_html_escape(a.get('property', ''))}</span>"
            f"<span class='assumption-meta'>"
            f"{_html_escape(a.get('source_type', ''))}: {_html_escape(a.get('source_ref', ''))}<br>"
            f"<code>{_html_escape(a.get('evidence_id', ''))}</code>"
            f"</span>"
            f"</li>"
        )
    return f"<ul class='assumption-list'>{''.join(items)}</ul>"


# ---------------------------------------------------------------------------
# Stage timeline
# ---------------------------------------------------------------------------

def _render_timeline(summary: Dict[str, Any]) -> str:
    """Render pipeline stage timeline with active/skipped indicators."""
    total = summary.get("total", 0)
    has_repair = summary.get("fixed", 0) > 0
    has_vulnerable = summary.get("vulnerable", 0) > 0 or has_repair

    stages = [
        ("🔍", "Discover", "Obligations &amp; invariants", True),
        ("🔄", "Translate", "Python → Lean 4 / Dafny", True),
        ("⚖️", "Verify", "Formal proof check", True),
        ("🔬", "Proof&nbsp;Search", "LLM-guided tactics", has_vulnerable),
        ("🔧", "Repair", "Claude generates fix", has_repair),
        ("✅", "Re-verify", "Proof confirmed", has_repair),
        ("📢", "Enforce", "MR gate &amp; artifacts", True),
    ]

    parts = []
    for i, (icon, name, desc, active) in enumerate(stages):
        box_class = "stage-box" + ("" if active else " skipped")
        style_attr = " style='border-color:var(--verified)'" if active else ""
        arrow_html = "<div class='stage-arrow'>→</div>" if i < len(stages) - 1 else ""
        parts.append(
            f"<div class='stage'>"
            f"<div class='{box_class}'{style_attr}>"
            f"<div class='stage-icon'>{icon}</div>"
            f"<div class='stage-name'>{name}</div>"
            f"<div class='stage-desc'>{desc}</div>"
            f"</div>"
            f"{arrow_html}"
            f"</div>"
        )
    return "".join(parts)


# ---------------------------------------------------------------------------
# File card renderer
# ---------------------------------------------------------------------------

def _render_file_card(
    idx: int,
    file_data: Dict[str, Any],
    trace_file: Optional[Dict[str, Any]] = None,
    lean_code: Optional[str] = None,
    original_code: Optional[str] = None,
    repaired_code: Optional[str] = None,
) -> str:
    verdict = file_data.get("verdict", "ERROR")
    filename = file_data.get("filename", "unknown")
    engine = file_data.get("engine", "n/a")
    message = file_data.get("message", "")
    obligations = file_data.get("obligations", [])
    assumptions = file_data.get("assumptions", [])

    # Get obligation results from trace file if available
    obligation_results = trace_file.get("obligation_results", []) if trace_file else []

    icon = _verdict_file_icon(verdict)

    # Message section
    msg_class = {"VULNERABLE": "vulnerable", "FIXED": "fixed", "VERIFIED": "verified"}.get(verdict, "")
    message_html = f"<div class='message-box {msg_class}'>{_html_escape(message or 'No detail available.')}</div>"

    # Action guidance
    action_html = _action_guidance(verdict, message, obligation_results)

    # Code panels
    code_sections = []
    if lean_code and original_code:
        code_sections.append(
            f"<div class='file-section'>"
            f"<div class='file-section-title'>Code Artifacts</div>"
            f"<div class='code-grid'>"
            f"{_render_code_panel('Source Code', original_code, 'python')}"
            f"{_render_code_panel('Lean 4 Proof Obligations', lean_code, 'lean')}"
            f"</div>"
            f"</div>"
        )
    elif original_code and repaired_code:
        code_sections.append(
            f"<div class='file-section'>"
            f"<div class='file-section-title'>Repair Diff — Before / After</div>"
            f"<div class='code-grid'>"
            f"{_render_code_panel('Original (Vulnerable)', original_code, 'python')}"
            f"{_render_code_panel('Repaired (Verified)', repaired_code, 'python', 'fixed')}"
            f"</div>"
            f"</div>"
        )
    elif original_code:
        code_sections.append(
            f"<div class='file-section'>"
            f"<div class='file-section-title'>Source Code</div>"
            f"{_render_code_panel('Source Code', original_code, 'python')}"
            f"</div>"
        )
    elif lean_code:
        code_sections.append(
            f"<div class='file-section'>"
            f"<div class='file-section-title'>Lean 4 Proof Obligations</div>"
            f"{_render_code_panel('Lean 4 Proof', lean_code, 'lean')}"
            f"</div>"
        )

    html = (
        f"<div class='file-card'>"
        f"<div class='file-header' onclick='toggleCard(this)'>"
        f"  <div class='file-info'>"
        f"    <span class='file-icon'>{icon}</span>"
        f"    <div>"
        f"      <div class='file-name'>{_html_escape(filename)}</div>"
        f"      <div class='file-engine'>Engine: {_html_escape(engine)}</div>"
        f"    </div>"
        f"  </div>"
        f"  <div class='file-right'>"
        f"    <span class='verdict-badge {verdict}'>{verdict}</span>"
        f"    <span class='chevron'>▼</span>"
        f"  </div>"
        f"</div>"
        f"<div class='file-body'>"
        f"  <div class='file-section'>"
        f"    <div class='file-section-title'>Verification Finding</div>"
        f"    {message_html}"
        f"    {action_html}"
        f"  </div>"
        f"  <div class='file-section'>"
        f"    <div class='file-section-title'>Security Obligations ({len(obligations)} total)</div>"
        f"    {_render_obligation_table(obligations, obligation_results)}"
        f"  </div>"
        f"  <div class='file-section'>"
        f"    <div class='file-section-title'>Assumed Inputs ({len(assumptions)} total)</div>"
        f"    {_render_assumptions_list(assumptions)}"
        f"  </div>"
        f"  {''.join(code_sections)}"
        f"</div>"
        f"</div>"
    )
    return html


# ---------------------------------------------------------------------------
# Trace artifact loader
# ---------------------------------------------------------------------------

def _load_trace_artifacts(
    trace_root: str,
    run_id: Optional[str],
    filenames: List[str],
) -> Dict[str, Any]:
    """Load per-file trace artifacts. Returns dict keyed by filename."""
    results: Dict[str, Any] = {}
    if not trace_root:
        return results

    root = Path(trace_root)
    if not root.exists():
        return results

    # Find run directory
    if run_id:
        run_dir = root / run_id
    else:
        # Auto-detect: use the most recent run directory
        try:
            run_dirs = sorted(
                [d for d in root.iterdir() if d.is_dir()],
                key=lambda d: d.stat().st_mtime,
                reverse=True,
            )
            run_dir = run_dirs[0] if run_dirs else None
        except Exception:
            run_dir = None

    if not run_dir or not run_dir.exists():
        return results

    files_dir = run_dir / "files"
    if not files_dir.exists():
        return results

    for fname in filenames:
        file_dir = files_dir / fname
        if not file_dir.exists():
            continue

        data: Dict[str, Any] = {}

        result_path = file_dir / "result.json"
        if result_path.exists():
            try:
                data["result"] = json.loads(result_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Load Lean proof code
        for lean_candidate in ["02_translation.lean"]:
            lean_path = file_dir / lean_candidate
            if lean_path.exists():
                try:
                    data["lean_code"] = lean_path.read_text(encoding="utf-8")
                except Exception:
                    pass
                break

        # Load repaired Python code
        for repair_candidate in ["04_repair_0.py", "04_repair_1.py"]:
            rep_path = file_dir / repair_candidate
            if rep_path.exists():
                try:
                    data["repaired_code"] = rep_path.read_text(encoding="utf-8")
                except Exception:
                    pass
                break

        results[fname] = data

    return results


def _load_manifest(trace_root: str, run_id: Optional[str]) -> Dict[str, Any]:
    """Load manifest.json for the given run."""
    root = Path(trace_root)
    if not root.exists():
        return {}

    if run_id:
        manifest_path = root / run_id / "manifest.json"
    else:
        try:
            run_dirs = sorted(
                [d for d in root.iterdir() if d.is_dir()],
                key=lambda d: d.stat().st_mtime,
                reverse=True,
            )
            manifest_path = run_dirs[0] / "manifest.json" if run_dirs else None
        except Exception:
            manifest_path = None

    if not manifest_path or not manifest_path.exists():
        return {}

    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Main HTML assembler
# ---------------------------------------------------------------------------

def generate_dashboard(
    report_path: str,
    trace_root: str = ".argus-trace",
    run_id: Optional[str] = None,
    output_path: str = "argus_dashboard.html",
    original_code: Optional[Dict[str, str]] = None,
) -> str:
    """
    Generate a self-contained HTML Mission Control dashboard.

    Args:
        report_path: Path to argus_report.json produced by the pipeline.
        trace_root: Directory containing .argus-trace/<run>/ subdirectories.
        run_id: Specific run ID to load. If None, the most recent run is used.
        output_path: Where to write argus_dashboard.html.
        original_code: Optional mapping of filename -> original Python source.

    Returns:
        The path where the dashboard was written.
    """
    # --- Load report ---
    report: Dict[str, Any] = {}
    try:
        report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    except Exception:
        pass

    files: List[Dict[str, Any]] = report.get("files", [])
    summary: Dict[str, Any] = report.get("summary", {})
    provider = report.get("provider", "")
    model = report.get("model", "")
    timestamp = report.get("timestamp", datetime.now(timezone.utc).isoformat())
    filenames = [f.get("filename", "") for f in files]

    # --- Load trace artifacts ---
    manifest = _load_manifest(trace_root, run_id)
    run_id_resolved = manifest.get("run_id", run_id or "unknown")
    trace_artifacts = _load_trace_artifacts(trace_root, run_id, filenames)

    # --- Risk analysis ---
    risk = _risk_level(summary)

    # --- Provider badge ---
    provider_label = ""
    if provider == "anthropic":
        provider_label = f"Anthropic {model}"
    elif provider == "gemini":
        provider_label = f"Google Gemini ({model})"
    elif provider:
        provider_label = f"{provider} ({model})"

    # --- Build header ---
    header_meta = [f'<span class="run-id">Run: {_html_escape(run_id_resolved[:16])}</span>']
    if timestamp:
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            header_meta.append(ts.strftime("%Y-%m-%d %H:%M UTC"))
        except Exception:
            header_meta.append(_html_escape(timestamp[:19]))
    if provider_label:
        header_meta.append(f'<span class="provider-badge">⚡ {_html_escape(provider_label)}</span>')
    header_meta.append('<span style="color:var(--lean)">Lean 4 / Dafny</span>')

    # --- Build summary cards ---
    def count_card(cls: str, label: str, key: str) -> str:
        return (
            f"<div class='count-card {cls}'>"
            f"<div class='number'>{summary.get(key, 0)}</div>"
            f"<div class='label'>{label}</div>"
            f"</div>"
        )

    verdict_counts_html = (
        count_card("verified", "Verified", "verified")
        + count_card("fixed", "Auto-Repaired", "fixed")
        + count_card("vulnerable", "Vulnerable", "vulnerable")
        + count_card("unverified", "Unverified", "unverified")
        + count_card("error", "Error", "error")
    )

    # --- Build file cards ---
    file_cards_html = ""
    for idx, file_data in enumerate(files):
        fname = file_data.get("filename", "")
        artifacts = trace_artifacts.get(fname, {})
        trace_result = artifacts.get("result", {})
        lean_code = artifacts.get("lean_code")
        orig = (original_code or {}).get(fname)
        repaired = artifacts.get("repaired_code")

        file_cards_html += _render_file_card(
            idx=idx,
            file_data=file_data,
            trace_file=trace_result,
            lean_code=lean_code,
            original_code=orig,
            repaired_code=repaired,
        )

    if not file_cards_html:
        file_cards_html = "<div style='color:var(--text-muted);padding:24px;text-align:center;'>No files were audited in this run.</div>"

    # --- Build audit trail ---
    config = manifest.get("config", {})
    audit_items = [
        ("Provider", provider_label or "n/a"),
        ("Model", model or config.get("model", "n/a")),
        ("Run ID", run_id_resolved),
        ("Timestamp", timestamp[:19] if timestamp else "n/a"),
        ("Files Audited", str(summary.get("total", len(files)))),
        ("Max Repair Attempts", str(config.get("max_repair_attempts", "n/a"))),
        ("Proof Search", str(config.get("allow_proof_search", "n/a"))),
        ("Trace Root", _html_escape(str(trace_root))),
    ]
    audit_grid_html = "".join(
        f"<div class='audit-item'><div class='audit-item-label'>{label}</div><div class='audit-item-value'>{_html_escape(str(value))}</div></div>"
        for label, value in audit_items
    )

    # --- Embed data for JS ---
    embedded_data = json.dumps({
        "run_id": run_id_resolved,
        "provider": provider,
        "model": model,
        "summary": summary,
        "risk": risk,
    }, indent=2)

    # --- Assemble full HTML ---
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ArgusV2 Mission Control — {_html_escape(run_id_resolved[:16])}</title>
<style>{_CSS}</style>
</head>
<body>

<!-- Header -->
<header class="header">
  <div class="header-brand">
    <div class="header-logo">A</div>
    <div>
      <div class="header-title">ArgusV2 Mission Control</div>
      <div class="header-subtitle">Autonomous DevSecOps Verification</div>
    </div>
  </div>
  <div class="header-meta">
    {'  '.join(f'<span>{m}</span>' for m in header_meta)}
  </div>
</header>

<div class="container">

<!-- Executive Summary -->
<div class="exec-summary">
  <h2>Executive Summary</h2>
  <div class="exec-tagline {risk}">{_exec_tagline(summary)}</div>
  <div class="verdict-counts">
    {verdict_counts_html}
  </div>
  <div>
    <span class="risk-badge {risk}">{_risk_label(risk)}</span>
  </div>
</div>

<!-- Pipeline Timeline -->
<div class="timeline">
  <h2>Pipeline Stages</h2>
  <div class="timeline-stages">
    {_render_timeline(summary)}
  </div>
</div>

<!-- File Results -->
<div class="section-title">File Verification Results</div>
{file_cards_html}

<!-- Audit Trail -->
<div class="audit-trail">
  <h2>Audit Trail &amp; Provenance</h2>
  <div class="audit-grid">
    {audit_grid_html}
  </div>
</div>

</div>

<!-- Footer -->
<footer class="footer">
  <div>
    <span class="footer-brand">ArgusV2</span> — Autonomous DevSecOps Agent
    &nbsp;·&nbsp; Claude proposes. Lean disposes. Argus enforces.
  </div>
  <div>Version 2.1.0 · CC0 License</div>
</footer>

<!-- Embedded data for JS (no external fetch) -->
<script type="application/json" id="argus-data">{embedded_data}</script>
<script>{_JS}</script>
</body>
</html>"""

    # --- Write output ---
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out)
