from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .models import AssumedInput, Obligation, Verdict


@dataclass
class FileReport:
    filename: str
    verdict: Verdict
    obligations: List[Obligation]
    assumptions: List[AssumedInput]
    engine: str
    message: str


# ---------------------------------------------------------------------------
# JSON report (machine-readable, unchanged format)
# ---------------------------------------------------------------------------

def render_json_report(
    files: List[FileReport],
    provider: str = "",
    model: str = "",
) -> Dict[str, Any]:
    payload = {
        "tool": "ArgusV2",
        "provider": provider,
        "model": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(files),
            "verified": sum(1 for item in files if item.verdict == Verdict.VERIFIED),
            "fixed": sum(1 for item in files if item.verdict == Verdict.FIXED),
            "vulnerable": sum(1 for item in files if item.verdict == Verdict.VULNERABLE),
            "unverified": sum(1 for item in files if item.verdict == Verdict.UNVERIFIED),
            "error": sum(1 for item in files if item.verdict == Verdict.ERROR),
        },
        "files": [
            {
                "filename": item.filename,
                "verdict": item.verdict.value,
                "engine": item.engine,
                "message": item.message,
                "obligations": [o.to_dict() for o in item.obligations],
                "assumptions": [a.to_dict() for a in item.assumptions],
            }
            for item in files
        ],
    }
    return payload


# ---------------------------------------------------------------------------
# Markdown audit report (enhanced with executive summary + risk assessment)
# ---------------------------------------------------------------------------

def render_markdown_report(
    files: List[FileReport],
    provider: str = "",
    model: str = "",
    repaired_code: Optional[Dict[str, str]] = None,
    original_code: Optional[Dict[str, str]] = None,
) -> str:
    repaired_code = repaired_code or {}
    original_code = original_code or {}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    verified_count = sum(1 for f in files if f.verdict == Verdict.VERIFIED)
    fixed_count = sum(1 for f in files if f.verdict == Verdict.FIXED)
    vuln_count = sum(1 for f in files if f.verdict == Verdict.VULNERABLE)
    unverified_count = sum(1 for f in files if f.verdict == Verdict.UNVERIFIED)
    error_count = sum(1 for f in files if f.verdict == Verdict.ERROR)
    total = len(files)

    # Risk level
    if vuln_count > 0 or error_count > 0:
        risk_level = "CRITICAL"
        risk_desc = "One or more critical vulnerabilities were detected. Do not merge until resolved."
    elif unverified_count > 0 or fixed_count > 0:
        risk_level = "ATTENTION REQUIRED"
        risk_desc = "Auto-repaired or unverified files require human review before merging."
    else:
        risk_level = "CLEAR"
        risk_desc = "All audited files passed formal verification. Safe to merge."

    # Executive summary paragraph
    if total == 0:
        exec_summary = "No Python files were audited in this run."
    elif verified_count == total:
        exec_summary = (
            f"All {total} audited file{'s' if total != 1 else ''} passed formal verification. "
            f"No security vulnerabilities were detected."
        )
    else:
        parts = []
        if vuln_count:
            parts.append(f"{vuln_count} vulnerability{'s require' if vuln_count != 1 else ' requires'} attention")
        if fixed_count:
            parts.append(f"{fixed_count} vulnerability{'s were' if fixed_count != 1 else ' was'} automatically repaired and re-verified")
        if verified_count:
            parts.append(f"{verified_count} file{'s passed' if verified_count != 1 else ' passed'} formal verification")
        if unverified_count:
            parts.append(f"{unverified_count} file{'s could' if unverified_count != 1 else ' could'} not be verified (manual review required)")
        exec_summary = ". ".join(parts).capitalize() + "." if parts else f"{total} files audited."

    provider_line = ""
    if provider:
        provider_label = f"Anthropic {model}" if provider == "anthropic" else f"Google Gemini ({model})"
        provider_line = f"\n**Reasoning Provider**: {provider_label}  \n**Verification Engine**: Lean 4 / Dafny"

    lines = [
        "# ArgusV2 Formal Verification Audit Report",
        "",
        f"**Generated**: {now}{provider_line}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        exec_summary,
        "",
        f"**Risk Level**: {risk_level} — {risk_desc}",
        "",
        "---",
        "",
        "## Verdict Summary",
        "",
        "| File | Verdict | Engine | Finding |",
        "|:---|:---|:---|:---|",
    ]
    for item in files:
        lines.append(
            f"| `{item.filename}` | **{item.verdict.value}** | {item.engine} "
            f"| {item.message or 'n/a'} |"
        )

    lines += ["", "---", "", "## Detailed Analysis", ""]

    for item in files:
        lines.append(f"### `{item.filename}`")
        lines.append("")

        verdict_icon = {
            Verdict.VERIFIED: "✅",
            Verdict.FIXED: "🔧",
            Verdict.VULNERABLE: "🚨",
            Verdict.UNVERIFIED: "⚠️",
            Verdict.ERROR: "💥",
        }.get(item.verdict, "❓")

        lines.append(f"**Verdict**: {verdict_icon} {item.verdict.value}  ")
        lines.append(f"**Engine**: `{item.engine}`  ")
        lines.append(f"**Finding**: {item.message or 'n/a'}")
        lines.append("")

        # Action items for non-VERIFIED
        if item.verdict == Verdict.VULNERABLE:
            lines.append("> **Action Required**: Review the failing obligations below.")
            lines.append("> Add the missing invariant or bounds check, then re-push to trigger re-verification.")
            lines.append("")
        elif item.verdict == Verdict.FIXED:
            lines.append("> **Auto-Repaired**: Argus detected a vulnerability and generated a verified repair.")
            lines.append("> Review the repaired code before merging.")
            lines.append("")
        elif item.verdict == Verdict.UNVERIFIED:
            lines.append("> **Manual Review Required**: Argus could not verify this file.")
            lines.append("> Ensure a security engineer reviews the logic manually.")
            lines.append("")

        # Obligations
        if item.obligations:
            lines.append("#### Security Obligations")
            lines.append("")
            lines.append("| ID | Property | Severity | Status |")
            lines.append("|:---|:---|:---|:---|")
            for obl in item.obligations:
                # For vulnerable files mark them as failed; otherwise pass
                status = "FAIL" if item.verdict == Verdict.VULNERABLE else "PASS"
                lines.append(
                    f"| `{obl.id}` | `{obl.property}` | {obl.severity.value.upper()} | {status} |"
                )
            lines.append("")

        # Assumptions
        if item.assumptions:
            lines.append("#### Assumed Inputs")
            lines.append("")
            lines.append("| Property | Source | Evidence ID |")
            lines.append("|:---|:---|:---|")
            for a in item.assumptions:
                lines.append(f"| `{a.property}` | {a.source_type}: {a.source_ref} | `{a.evidence_id}` |")
            lines.append("")

        # Repair diff for FIXED files
        if item.verdict == Verdict.FIXED:
            orig = original_code.get(item.filename)
            rep = repaired_code.get(item.filename)
            if orig and rep:
                lines.append("#### Repair: Before / After")
                lines.append("")
                lines.append("**Original (vulnerable)**:")
                lines.append("```python")
                lines.append(orig.rstrip())
                lines.append("```")
                lines.append("")
                lines.append("**Repaired (formally verified)**:")
                lines.append("```python")
                lines.append(rep.rstrip())
                lines.append("```")
                lines.append("")

        lines.append("---")
        lines.append("")

    # Risk Assessment section
    lines += [
        "## Risk Assessment",
        "",
        f"**Overall Risk Level**: {risk_level}",
        "",
        "| Verdict | Count | Meaning |",
        "|:---|:---|:---|",
        f"| VERIFIED | {verified_count} | Formally proven safe — all obligations pass |",
        f"| FIXED | {fixed_count} | Vulnerability found and automatically repaired |",
        f"| VULNERABLE | {vuln_count} | Obligation failed — merge should be blocked |",
        f"| UNVERIFIED | {unverified_count} | Unsupported constructs — manual review required |",
        f"| ERROR | {error_count} | Tooling/runtime error — re-run or escalate |",
        "",
        "---",
        "",
        "## Recommendations",
        "",
    ]

    if vuln_count > 0:
        lines.append("1. **Block merge** — At least one file has unresolved vulnerabilities.")
        lines.append("2. Apply the suggested fix for each VULNERABLE file, or open a follow-up MR with the repair.")
        lines.append("3. Re-push to trigger Argus re-verification.")
    if fixed_count > 0:
        lines.append("1. **Review auto-repaired code** — Argus generated and verified a fix, but human review is good practice.")
        lines.append("2. Confirm the repaired logic matches business intent before merging.")
    if unverified_count > 0:
        lines.append("1. **Manually audit UNVERIFIED files** — Argus could not verify these due to unsupported constructs.")
        lines.append("2. Consider refactoring to simpler patterns Argus can verify, or document the manual review outcome.")
    if vuln_count == 0 and fixed_count == 0 and unverified_count == 0:
        lines.append("1. **Merge safely** — All files passed formal verification.")
        lines.append("2. Download this report as a compliance artifact for your audit trail.")

    lines += [
        "",
        "---",
        "",
        "## Audit Metadata",
        "",
        f"- **Tool**: ArgusV2 v2.1.0",
    ]
    if provider_line:
        lines.append(f"- **Provider**: {provider_label if provider else 'n/a'}")
        lines.append(f"- **Model**: {model}")
    lines += [
        f"- **Timestamp**: {now}",
        f"- **Files Audited**: {total}",
        "",
        "_Generated by ArgusV2 — Claude proposes. Lean disposes. Argus enforces._",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MR comment (enhanced: executive summary + grouped verdicts + action items)
# ---------------------------------------------------------------------------

def render_mr_comment(
    files: List[FileReport],
    provider: str = "",
    model: str = "",
    repaired_code: Optional[Dict[str, str]] = None,
    original_code: Optional[Dict[str, str]] = None,
) -> str:
    repaired_code = repaired_code or {}
    original_code = original_code or {}

    verified = [f for f in files if f.verdict == Verdict.VERIFIED]
    fixed = [f for f in files if f.verdict == Verdict.FIXED]
    vulnerable = [f for f in files if f.verdict == Verdict.VULNERABLE]
    unverified = [f for f in files if f.verdict == Verdict.UNVERIFIED]
    error = [f for f in files if f.verdict == Verdict.ERROR]

    total = len(files)

    # Executive summary line
    if total == 0:
        exec_line = "No Python files were audited."
    elif len(verified) == total:
        exec_line = f"All {total} audited file{'s' if total != 1 else ''} passed formal verification."
    else:
        parts = []
        if vulnerable:
            parts.append(f"**{len(vulnerable)} vulnerability** detected")
        if fixed:
            parts.append(f"**{len(fixed)} automatically repaired** and re-verified")
        if verified:
            parts.append(f"{len(verified)} verified safe")
        exec_line = ", ".join(parts) + "." if parts else f"{total} files audited."

    lines = [
        "## Argus Formal Verification Report",
        "",
        f"**Executive Summary**: {exec_line}",
        "",
        f"| Verified | Auto-Repaired | Vulnerable | Unverified/Error |",
        f"|:---:|:---:|:---:|:---:|",
        f"| {len(verified)} | {len(fixed)} | {len(vulnerable)} | {len(unverified) + len(error)} |",
        "",
    ]

    # Action Required section
    if vulnerable or error:
        lines.append("---")
        lines.append("")
        lines.append("### Action Required")
        lines.append("")
        for item in vulnerable + error:
            lines.append(f"**`{item.filename}`** — {item.verdict.value}")
            lines.append("")
            if item.message:
                lines.append(f"> {item.message}")
                lines.append("")
            # Obligation details (collapsible)
            if item.obligations:
                lines.append("<details>")
                lines.append(f"<summary>Obligations ({len(item.obligations)} total — expand for details)</summary>")
                lines.append("")
                lines.append("| Obligation | Property | Severity |")
                lines.append("|:---|:---|:---|")
                for obl in item.obligations:
                    lines.append(f"| `{obl.id}` | `{obl.property}` | {obl.severity.value.upper()} |")
                lines.append("")
                lines.append("</details>")
                lines.append("")

    # Auto-Repaired section
    if fixed:
        lines.append("---")
        lines.append("")
        lines.append("### Auto-Repaired")
        lines.append("")
        for item in fixed:
            lines.append(f"**`{item.filename}`** — FIXED")
            lines.append("")
            lines.append("> Argus detected a vulnerability and generated a formally verified repair.")
            lines.append("")
            # Repair diff
            orig = original_code.get(item.filename)
            rep = repaired_code.get(item.filename)
            if orig and rep:
                lines.append("<details>")
                lines.append("<summary>View repair diff</summary>")
                lines.append("")
                orig_lines_set = set(orig.splitlines())
                rep_lines_set = set(rep.splitlines())
                diff_lines = []
                for ln in orig.splitlines():
                    if ln not in rep_lines_set:
                        diff_lines.append(f"- {ln}")
                for ln in rep.splitlines():
                    if ln not in orig_lines_set:
                        diff_lines.append(f"+ {ln}")
                if diff_lines:
                    lines.append("```diff")
                    lines.extend(diff_lines)
                    lines.append("```")
                else:
                    lines.append("```python")
                    lines.append(rep.rstrip())
                    lines.append("```")
                lines.append("")
                lines.append("</details>")
                lines.append("")
            # Obligation confirmation
            if item.obligations:
                lines.append("<details>")
                lines.append("<summary>Verified obligations</summary>")
                lines.append("")
                lines.append("| Obligation | Property | Status |")
                lines.append("|:---|:---|:---|")
                for obl in item.obligations:
                    lines.append(f"| `{obl.id}` | `{obl.property}` | PASS |")
                lines.append("")
                lines.append("</details>")
                lines.append("")

    # Unverified section
    if unverified:
        lines.append("---")
        lines.append("")
        lines.append("### Unverified (Manual Review Required)")
        lines.append("")
        for item in unverified:
            lines.append(f"**`{item.filename}`** — UNVERIFIED")
            lines.append("")
            if item.message:
                lines.append(f"> {item.message}")
                lines.append("")

    # Verified section
    if verified:
        lines.append("---")
        lines.append("")
        lines.append("### Verified")
        lines.append("")
        lines.append("| File | Obligations Passed | Engine |")
        lines.append("|:---|:---|:---|")
        for item in verified:
            lines.append(
                f"| `{item.filename}` | {len(item.obligations)} | {item.engine} |"
            )
        lines.append("")

    # Provider footer
    lines.append("---")
    lines.append("")
    if provider:
        provider_label = f"Anthropic {model}" if provider == "anthropic" else f"Google Gemini ({model})"
        lines.append(
            f"**Reasoning**: {provider_label} &nbsp;·&nbsp; "
            f"**Verification**: Lean 4 / Dafny &nbsp;·&nbsp; "
            f"**Trust model**: Claude proposes — Lean disposes — Argus enforces"
        )
    else:
        lines.append("**Verification Engine**: Lean 4 / Dafny")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SARIF report (unchanged format — machine-readable standard)
# ---------------------------------------------------------------------------

def render_sarif_report(
    files: List[FileReport],
    provider: str = "",
    model: str = "",
) -> Dict[str, Any]:
    """SARIF 2.1.0 output focused on actionable non-VERIFIED outcomes."""
    rules = [
        {
            "id": "argus/vulnerable",
            "name": "Argus Vulnerability",
            "shortDescription": {"text": "Canonical obligations failed"},
            "fullDescription": {"text": "Argus could not prove one or more obligations."},
            "defaultConfiguration": {"level": "error"},
        },
        {
            "id": "argus/unverified",
            "name": "Argus Unverified",
            "shortDescription": {"text": "Verification was inconclusive"},
            "fullDescription": {"text": "Argus could not verify due to unsupported constructs or guard failures."},
            "defaultConfiguration": {"level": "warning"},
        },
        {
            "id": "argus/error",
            "name": "Argus Verification Error",
            "shortDescription": {"text": "Tooling/runtime verification error"},
            "fullDescription": {"text": "Argus encountered a verifier/runtime error and failed closed."},
            "defaultConfiguration": {"level": "error"},
        },
    ]

    results: List[Dict[str, Any]] = []
    for item in files:
        if item.verdict not in {Verdict.VULNERABLE, Verdict.UNVERIFIED, Verdict.ERROR}:
            continue
        rule_id = f"argus/{item.verdict.value.lower()}"
        level = "error" if item.verdict in {Verdict.VULNERABLE, Verdict.ERROR} else "warning"
        results.append(
            {
                "ruleId": rule_id,
                "level": level,
                "message": {"text": item.message or item.verdict.value},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": item.filename},
                            "region": {"startLine": 1},
                        }
                    }
                ],
                "properties": {
                    "argus_verdict": item.verdict.value,
                    "engine": item.engine,
                    "obligation_count": len(item.obligations),
                },
            }
        )

    driver_properties: Dict[str, Any] = {}
    if provider:
        driver_properties["provider"] = provider
        driver_properties["model"] = model

    driver: Dict[str, Any] = {
        "name": "ArgusV2",
        "version": "2.1.0",
        "informationUri": "https://gitlab.com",
        "rules": rules,
    }
    if driver_properties:
        driver["properties"] = driver_properties

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": driver},
                "results": results,
            }
        ],
    }


# ---------------------------------------------------------------------------
# GitLab SAST report (unchanged format)
# ---------------------------------------------------------------------------

def render_gitlab_sast_report(files: List[FileReport]) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    vulnerabilities: List[Dict[str, Any]] = []

    for item in files:
        if item.verdict not in {Verdict.VULNERABLE, Verdict.UNVERIFIED, Verdict.ERROR}:
            continue

        fingerprint = hashlib.sha256(
            f"{item.filename}:{item.verdict.value}:{item.message}".encode("utf-8")
        ).hexdigest()
        vulnerabilities.append(
            {
                "id": fingerprint,
                "category": "sast",
                "name": f"Argus {item.verdict.value}",
                "message": item.message or f"Argus reported {item.verdict.value}",
                "description": item.message or f"Argus reported {item.verdict.value} for {item.filename}",
                "severity": _gitlab_severity(item.verdict),
                "confidence": "High",
                "scanner": {
                    "id": "argus-v2",
                    "name": "ArgusV2",
                },
                "location": {
                    "file": item.filename,
                    "start_line": 1,
                },
                "identifiers": [
                    {
                        "type": "argus_rule",
                        "name": f"argus/{item.verdict.value.lower()}",
                        "value": f"argus/{item.verdict.value.lower()}",
                    }
                ],
            }
        )

    return {
        "version": "15.0.7",
        "scan": {
            "type": "sast",
            "start_time": now_iso,
            "end_time": now_iso,
            "status": "success",
            "analyzer": {
                "id": "argus-v2",
                "name": "ArgusV2",
                "version": "2.0.0",
                "vendor": {"name": "Argus"},
            },
            "scanner": {
                "id": "argus-v2",
                "name": "ArgusV2",
                "version": "2.0.0",
                "vendor": {"name": "Argus"},
            },
        },
        "vulnerabilities": vulnerabilities,
        "remediations": [],
    }


def _gitlab_severity(verdict: Verdict) -> str:
    if verdict in {Verdict.VULNERABLE, Verdict.ERROR}:
        return "Critical"
    if verdict == Verdict.UNVERIFIED:
        return "High"
    return "Info"


def dump_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
