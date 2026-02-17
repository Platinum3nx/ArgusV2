from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class SecretFinding:
    file_path: str
    line_number: int
    kind: str
    snippet: str


PATTERNS = {
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "generic_api_key": re.compile(r"(?i)\b(api[_-]?key|token|secret)\s*[:=]\s*['\"][^'\"]{10,}['\"]"),
}


def scan_text(content: str, file_path: str) -> List[SecretFinding]:
    findings: List[SecretFinding] = []
    for idx, line in enumerate(content.splitlines(), start=1):
        for kind, pattern in PATTERNS.items():
            if pattern.search(line):
                findings.append(
                    SecretFinding(
                        file_path=file_path,
                        line_number=idx,
                        kind=kind,
                        snippet=line.strip()[:200],
                    )
                )
    return findings


def scan_files(paths: List[Path], repo_root: Path) -> List[SecretFinding]:
    findings: List[SecretFinding] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        findings.extend(scan_text(text, str(path.relative_to(repo_root))))
    return findings

