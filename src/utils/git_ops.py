from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List


def changed_python_files(repo_root: Path, base_ref: str | None = None) -> List[str]:
    if base_ref:
        cmd = ["git", "diff", "--name-only", base_ref, "HEAD"]
    else:
        cmd = ["git", "diff", "--name-only", "HEAD^", "HEAD"]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return []

    paths = []
    for line in result.stdout.splitlines():
        if line.endswith(".py") and (repo_root / line).exists():
            paths.append(line)
    return paths

