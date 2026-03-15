from __future__ import annotations

import json
from pathlib import Path

from src.core.ci_integrity import run_ci_integrity_suite
from src.core.pipeline import ArgusPipeline, PipelineConfig
from src.core.reporter import FileReport


def load_seeded_cases(repo_root: Path) -> list[tuple[str, str]]:
    bench = repo_root / "benchmarks" / "seeded"
    manifest = json.loads((bench / "manifest.json").read_text(encoding="utf-8"))
    out: list[tuple[str, str]] = []
    for case in manifest.get("cases", []):
        rel = case["path"]
        out.append((f"benchmarks/seeded/{rel}", (bench / rel).read_text(encoding="utf-8")))
    return out


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    out_dir = repo / "artifacts" / "phase1"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = load_seeded_cases(repo)
    pipeline = ArgusPipeline(
        config=PipelineConfig(
            allow_repair=True,
            allow_proof_search=True,
            require_docker_verify=False,
            trace_root=str(repo / ".argus-trace"),
        )
    )

    reports = pipeline.run_many(files)
    gate_report = run_ci_integrity_suite(
        files=files,
        reports=reports,
        trace_root=Path(pipeline.config.trace_root),
        run_id=pipeline.last_run_id,
        benchmark_root=repo / "benchmarks" / "seeded",
    )

    payload = gate_report.to_dict()
    payload["run_id"] = pipeline.last_run_id
    payload["report_files"] = [
        {
            "filename": r.filename,
            "verdict": r.verdict.value,
            "engine": r.engine,
            "message": r.message,
        }
        for r in reports
    ]

    (out_dir / "ci-gates.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if gate_report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
