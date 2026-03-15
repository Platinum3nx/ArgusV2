from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from src.core.pipeline import ArgusPipeline, PipelineConfig


def load_seeded_cases(repo_root: Path) -> list[tuple[str, str]]:
    bench = repo_root / "benchmarks" / "seeded"
    manifest = json.loads((bench / "manifest.json").read_text(encoding="utf-8"))
    cases: list[tuple[str, str]] = []
    for case in manifest.get("cases", []):
        rel = case["path"]
        code = (bench / rel).read_text(encoding="utf-8")
        cases.append((f"benchmarks/seeded/{rel}", code))
    return cases


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "artifacts" / "phase1"
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = load_seeded_cases(repo_root)
    runs = 20
    all_latencies: list[float] = []
    verdict_matrix: dict[str, list[str]] = {name: [] for name, _ in cases}
    failures: list[str] = []

    for run in range(1, runs + 1):
        pipeline = ArgusPipeline(
            config=PipelineConfig(
                allow_repair=True,
                allow_proof_search=True,
                require_docker_verify=False,
                trace_root=str(repo_root / ".argus-trace"),
            )
        )

        for name, code in cases:
            t0 = time.perf_counter()
            result = pipeline.run_file(name, code)
            dt = (time.perf_counter() - t0) * 1000.0
            all_latencies.append(dt)
            verdict_matrix[name].append(result.verdict.value)

            if result.verdict.value in {"ERROR", "UNVERIFIED"}:
                failures.append(f"run={run} file={name} verdict={result.verdict.value} msg={result.message}")

    stability = {
        name: len(set(values)) == 1 for name, values in verdict_matrix.items()
    }
    summary = {
        "runs": runs,
        "files_per_run": len(cases),
        "total_file_executions": runs * len(cases),
        "p50_latency_ms": round(statistics.median(all_latencies), 2),
        "p95_latency_ms": round(statistics.quantiles(all_latencies, n=100)[94], 2),
        "max_latency_ms": round(max(all_latencies), 2),
        "verdict_stability": stability,
        "all_stable": all(stability.values()),
        "error_or_unverified_count": len(failures),
    }

    (out_dir / "reliability-summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    (out_dir / "reliability-failures.log").write_text(
        "\n".join(failures), encoding="utf-8"
    )

    print(json.dumps(summary, indent=2))
    return 0 if summary["error_or_unverified_count"] == 0 and summary["all_stable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
