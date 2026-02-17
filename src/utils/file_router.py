from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import pathspec


def load_argusignore(repo_root: Path) -> pathspec.PathSpec:
    ignore_file = repo_root / ".argusignore"
    if not ignore_file.exists():
        return pathspec.PathSpec.from_lines("gitwildmatch", [])
    return pathspec.PathSpec.from_lines("gitwildmatch", ignore_file.read_text(encoding="utf-8").splitlines())


def discover_python_files(repo_root: Path, extra_excludes: Iterable[str] | None = None) -> List[Path]:
    spec = load_argusignore(repo_root)
    excludes = set(extra_excludes or [])
    files: List[Path] = []
    for path in repo_root.rglob("*.py"):
        rel = path.relative_to(repo_root).as_posix()
        if any(part in {"venv", "__pycache__", ".git", "legacy"} for part in path.parts):
            continue
        if rel in excludes or spec.match_file(rel):
            continue
        files.append(path)
    return files

