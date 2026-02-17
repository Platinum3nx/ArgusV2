from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from .models import AssumedInput, Obligation, Verdict


@dataclass
class FileReport:
    filename: str
    verdict: Verdict
    obligations: List[Obligation]
    assumptions: List[AssumedInput]
    engine: str
    message: str


def render_json_report(files: List[FileReport]) -> Dict[str, Any]:
    payload = {
        "tool": "ArgusV2",
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


def render_markdown_report(files: List[FileReport]) -> str:
    lines = [
        "# ArgusV2 Verification Report",
        "",
        "| File | Verdict | Engine |",
        "|:---|:---|:---|",
    ]
    for item in files:
        lines.append(f"| `{item.filename}` | {item.verdict.value} | {item.engine} |")

    lines.append("")
    for item in files:
        lines.append(f"## {item.filename}")
        lines.append(f"- Verdict: **{item.verdict.value}**")
        lines.append(f"- Engine: `{item.engine}`")
        lines.append(f"- Message: {item.message or 'n/a'}")
        lines.append("- Obligations:")
        for obligation in item.obligations:
            lines.append(f"  - `{obligation.id}`: {obligation.property}")
        lines.append("- Assumptions:")
        for assumption in item.assumptions:
            lines.append(
                f"  - `{assumption.property}` ({assumption.source_type}:{assumption.source_ref})"
            )
        lines.append("")
    return "\n".join(lines)


def render_mr_comment(files: List[FileReport]) -> str:
    report = render_json_report(files)
    summary = report["summary"]
    lines = [
        "## 🛡️ Argus Formal Verification Report",
        "",
        (
            f"**Files Audited**: {summary['total']} | "
            f"✅ Verified: {summary['verified']} | "
            f"🔧 Fixed: {summary['fixed']} | "
            f"❌ Vulnerable: {summary['vulnerable']} | "
            f"⛔ Unverified/Error: {summary['unverified'] + summary['error']}"
        ),
        "",
        "| File | Verdict | Finding |",
        "|:---|:---|:---|",
    ]
    for item in files:
        lines.append(f"| `{item.filename}` | {item.verdict.value} | {item.message or 'n/a'} |")
    return "\n".join(lines)


def dump_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)

