from __future__ import annotations

import hashlib
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


def render_sarif_report(files: List[FileReport]) -> Dict[str, Any]:
    """
    SARIF 2.1.0 output focused on actionable non-VERIFIED outcomes.
    """
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

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "ArgusV2",
                        "version": "2.0.0",
                        "informationUri": "https://gitlab.com",
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }


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
