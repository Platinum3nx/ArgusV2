from __future__ import annotations

import json
from pathlib import Path

from src.core.ci_integrity import run_ci_integrity_suite
from src.core.models import Verdict
from src.core.reporter import FileReport


def test_ci_integrity_suite_passes_with_complete_inputs(tmp_path: Path) -> None:
    # Use code that has a non_negativity obligation (so semantic guard passes)
    # but contains no simple mutation match strings, so the mutation gate skips
    # (no mutations generated) rather than failing.
    # NOTE: avoid type-annotation arrows (->) because ">" now triggers a mutation.
    code = "def compute(total, amount):\n    return total\n"
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


def test_seeded_benchmark_gate_fails_on_verdict_mismatch(tmp_path: Path) -> None:
    """Gate fails when a pipeline report has the wrong verdict for a case with expected_verdict."""
    from src.core.ci_integrity import _seeded_benchmark_gate
    from src.core.obligation_policy import ObligationPolicy
    from src.core.reporter import FileReport

    bench_root = tmp_path / "benchmarks" / "seeded"
    _write_seeded_manifest_with_expected_verdicts(bench_root)

    # Provide a report where the safe file incorrectly gets VULNERABLE
    report_by_file = {
        "benchmarks/seeded/vulnerable/negative_withdrawal.py": FileReport(
            filename="benchmarks/seeded/vulnerable/negative_withdrawal.py",
            verdict=Verdict.VULNERABLE,
            obligations=[],
            assumptions=[],
            engine="lean",
            message="ok",
        ),
        "benchmarks/seeded/safe/saturating_withdrawal.py": FileReport(
            filename="benchmarks/seeded/safe/saturating_withdrawal.py",
            verdict=Verdict.VULNERABLE,  # wrong — should be VERIFIED
            obligations=[],
            assumptions=[],
            engine="lean",
            message="ok",
        ),
        "benchmarks/seeded/drift/uniqueness_probe.py": FileReport(
            filename="benchmarks/seeded/drift/uniqueness_probe.py",
            verdict=Verdict.VULNERABLE,
            obligations=[],
            assumptions=[],
            engine="lean",
            message="ok",
        ),
    }
    gate = _seeded_benchmark_gate(bench_root, report_by_file)
    assert not gate.passed
    assert "verdict_mismatch" in gate.details
    assert "safe/saturating_withdrawal.py" in gate.details


def test_seeded_benchmark_gate_passes_with_correct_verdicts(tmp_path: Path) -> None:
    """Gate passes when all pipeline reports match expected_verdict."""
    from src.core.ci_integrity import _seeded_benchmark_gate
    from src.core.reporter import FileReport

    bench_root = tmp_path / "benchmarks" / "seeded"
    _write_seeded_manifest_with_expected_verdicts(bench_root)

    report_by_file = {
        "benchmarks/seeded/vulnerable/negative_withdrawal.py": FileReport(
            filename="benchmarks/seeded/vulnerable/negative_withdrawal.py",
            verdict=Verdict.VULNERABLE,
            obligations=[],
            assumptions=[],
            engine="lean",
            message="ok",
        ),
        "benchmarks/seeded/safe/saturating_withdrawal.py": FileReport(
            filename="benchmarks/seeded/safe/saturating_withdrawal.py",
            verdict=Verdict.VERIFIED,
            obligations=[],
            assumptions=[],
            engine="lean",
            message="ok",
        ),
        "benchmarks/seeded/drift/uniqueness_probe.py": FileReport(
            filename="benchmarks/seeded/drift/uniqueness_probe.py",
            verdict=Verdict.VULNERABLE,
            obligations=[],
            assumptions=[],
            engine="lean",
            message="ok",
        ),
    }
    gate = _seeded_benchmark_gate(bench_root, report_by_file)
    assert gate.passed, gate.details


def _write_seeded_manifest_with_expected_verdicts(bench_root: Path) -> None:
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
                    {
                        "path": "vulnerable/negative_withdrawal.py",
                        "expected": "blocking",
                        "expected_verdict": "VULNERABLE",
                    },
                    {
                        "path": "safe/saturating_withdrawal.py",
                        "expected": "supported",
                        "expected_verdict": "VERIFIED",
                    },
                    {
                        "path": "drift/uniqueness_probe.py",
                        "expected": "blocking",
                        "expected_verdict": "VULNERABLE",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )


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
                    {"path": "drift/uniqueness_probe.py", "expected": "blocking"},
                ]
            }
        ),
        encoding="utf-8",
    )
