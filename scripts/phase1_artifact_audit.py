from __future__ import annotations

import json
from pathlib import Path


REQUIRED_RUN_FILES = ["manifest.json", "summary.json"]
REQUIRED_FILE_ARTIFACTS = ["01_discovery.json", "result.json", "02_semantic_guard.json", "03_verify_stdout.txt"]


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    trace_root = repo / ".argus-trace"
    out_dir = repo / "artifacts" / "phase1"
    out_dir.mkdir(parents=True, exist_ok=True)

    run_dirs = sorted([p for p in trace_root.iterdir() if p.is_dir()]) if trace_root.exists() else []
    if not run_dirs:
        print(json.dumps({"ok": False, "reason": "no trace runs found"}, indent=2))
        return 1

    all_missing: list[str] = []
    total_checked_files = 0

    for run in run_dirs:
        run_missing: list[str] = []
        for req in REQUIRED_RUN_FILES:
            if not (run / req).exists():
                run_missing.append(req)

        files_root = run / "files"
        for result in files_root.rglob("result.json"):
            file_dir = result.parent
            rel = str(file_dir.relative_to(run))
            total_checked_files += 1
            for req in REQUIRED_FILE_ARTIFACTS:
                if not (file_dir / req).exists():
                    run_missing.append(f"{rel}/{req}")

        for item in run_missing:
            all_missing.append(f"{run.name}:{item}")

    payload = {
        "run_count": len(run_dirs),
        "checked_files": total_checked_files,
        "missing": all_missing,
        "ok": not all_missing,
    }
    (out_dir / "artifact-audit.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if not all_missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
