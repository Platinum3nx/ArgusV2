from __future__ import annotations

import json
from pathlib import Path

from src.core.ci_integrity import run_ci_integrity_suite
from src.core.models import Verdict
from src.core.reporter import FileReport


def test_ci_integrity_suite_passes_with_complete_inputs(tmp_path: Path) -> None:
    code = "def withdraw(balance: int, amount: int) -> int:\n    if amount >= 0:\n        return balance\n    return balance - amount\n"
    files = [("withdraw.py", code)]
    reports = [
        FileReport(
            filename="withdraw.py",
            verdict=Verdict.VERIFIED,
            obligations=[],
            assumptions=[],
            engine="lean",
            message="ok",
        )
    ]

    run_id = "run-1"
    run_dir = tmp_path / ".argus-trace" / run_id / "files" / "withdraw.py"
    run_dir.mkdir(parents=True)
    (tmp_path / ".argus-trace" / run_id / "manifest.json").write_text("{}", encoding="utf-8")
    (tmp_path / ".argus-trace" / run_id / "summary.json").write_text("{}", encoding="utf-8")
    (run_dir / "01_discovery.json").write_text(
        json.dumps({"unsupported_constructs": []}),
        encoding="utf-8",
    )
    (run_dir / "02_translation.lean").write_text("def withdraw (balance amount : Int) : Int := balance", encoding="utf-8")
    (run_dir / "03_verify_stdout.txt").write_text("ok", encoding="utf-8")
    (run_dir / "result.json").write_text("{}", encoding="utf-8")

    bench_root = tmp_path / "benchmarks" / "seeded"
    _write_seeded_manifest(bench_root)

    result = run_ci_integrity_suite(
        files=files,
        reports=reports,
        trace_root=tmp_path / ".argus-trace",
        run_id=run_id,
        benchmark_root=bench_root,
    )
    assert result.passed
    assert all(gate.passed for gate in result.gates)


def test_ci_integrity_suite_fails_traceability_without_run_id(tmp_path: Path) -> None:
    result = run_ci_integrity_suite(
        files=[("demo.py", "def demo(x: int) -> int:\n    return x\n")],
        reports=[
            FileReport(
                filename="demo.py",
                verdict=Verdict.VERIFIED,
                obligations=[],
                assumptions=[],
                engine="lean",
                message="ok",
            )
        ],
        trace_root=tmp_path / ".argus-trace",
        run_id=None,
        benchmark_root=None,
    )
    trace_gate = next(g for g in result.gates if g.name == "traceability-gate")
    assert not trace_gate.passed


def _write_seeded_manifest(bench_root: Path) -> None:
    (bench_root / "vulnerable").mkdir(parents=True, exist_ok=True)
    (bench_root / "safe").mkdir(parents=True, exist_ok=True)
    (bench_root / "drift").mkdir(parents=True, exist_ok=True)

    (bench_root / "vulnerable" / "negative_withdrawal.py").write_text(
        "def withdraw(balance: int, amount: int) -> int:\n    return balance - amount\n",
        encoding="utf-8",
    )
    (bench_root / "safe" / "saturating_withdrawal.py").write_text(
        "def withdraw(balance: int, amount: int) -> int:\n    if amount > balance:\n        return balance\n    return balance - amount\n",
        encoding="utf-8",
    )
    (bench_root / "drift" / "uniqueness_probe.py").write_text(
        "def append_unique(items: list[int], value: int) -> list[int]:\n    return items + [value]\n",
        encoding="utf-8",
    )
    (bench_root / "manifest.json").write_text(
        json.dumps(
            {
                "cases": [
                    {"path": "vulnerable/negative_withdrawal.py", "expected": "blocking"},
                    {"path": "safe/saturating_withdrawal.py", "expected": "supported"},
                    {"path": "drift/uniqueness_probe.py", "expected": "semantic_guard_failure"},
                ]
            }
        ),
        encoding="utf-8",
    )
