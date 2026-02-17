from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from .models import Verdict
from .obligation_policy import ObligationPolicy
from .quality_gates import (
    assumption_coverage_gate,
    mutation_kill_rate_gate,
    obligation_determinism_gate,
)
from .reporter import FileReport
from .semantic_guard import run_semantic_guard
from .translator import ASTTranslator, DafnyTranslator


@dataclass(frozen=True)
class CIGateResult:
    name: str
    passed: bool
    details: str


@dataclass(frozen=True)
class CIGateReport:
    passed: bool
    gates: List[CIGateResult]

    def to_dict(self) -> Dict[str, object]:
        return {
            "passed": self.passed,
            "gates": [
                {
                    "name": gate.name,
                    "passed": gate.passed,
                    "details": gate.details,
                }
                for gate in self.gates
            ],
        }


def run_ci_integrity_suite(
    files: Sequence[Tuple[str, str]],
    reports: Sequence[FileReport],
    trace_root: Path,
    run_id: str | None,
    benchmark_root: Path | None = None,
) -> CIGateReport:
    policy = ObligationPolicy()
    report_by_file = {item.filename: item for item in reports}

    unsupported_failures: List[str] = []
    determinism_failures: List[str] = []
    assumption_failures: List[str] = []
    semantic_failures: List[str] = []
    proof_failures: List[str] = []
    verdict_failures: List[str] = []
    reproducibility_failures: List[str] = []

    ast_translator = ASTTranslator()
    dafny_translator = DafnyTranslator()

    for filename, code in files:
        policy_result = policy.derive(code)
        report = report_by_file.get(filename)
        if report is None:
            proof_failures.append(f"{filename}:missing_pipeline_report")
            verdict_failures.append(f"{filename}:missing_pipeline_report")
            continue

        if policy_result.unsupported_constructs:
            unsupported_failures.append(
                f"{filename}:{','.join(policy_result.unsupported_constructs)}"
            )
            if report.verdict != Verdict.UNVERIFIED:
                verdict_failures.append(
                    f"{filename}:unsupported_constructs_must_be_unverified"
                )

        determinism = obligation_determinism_gate(code, policy=policy, runs=3)
        if not determinism.passed:
            determinism_failures.append(f"{filename}:{determinism.details}")

        reproducibility = obligation_determinism_gate(code, policy=policy, runs=2)
        if not reproducibility.passed:
            reproducibility_failures.append(f"{filename}:{reproducibility.details}")

        assumption_gate = assumption_coverage_gate(report.assumptions)
        if not assumption_gate.passed:
            assumption_failures.append(f"{filename}:{assumption_gate.details}")
            if report.verdict != Verdict.UNVERIFIED:
                verdict_failures.append(
                    f"{filename}:invalid_assumptions_must_be_unverified"
                )

        if not policy_result.unsupported_constructs:
            translation = (
                dafny_translator.translate(code, policy_result.obligations, report.assumptions)
                if _contains_loop(code)
                else ast_translator.translate(code, policy_result.obligations, report.assumptions)
            )
            if not translation.success:
                semantic_failures.append(f"{filename}:translation_failed")
            else:
                guard = run_semantic_guard(code, translation.code, policy_result.obligations)
                if not guard.passed:
                    semantic_failures.append(
                        f"{filename}:{','.join(issue.code for issue in guard.issues)}"
                    )

        if report.verdict not in {Verdict.VERIFIED, Verdict.FIXED}:
            proof_failures.append(f"{filename}:{report.verdict.value}")

    trace_gate = _traceability_gate(
        files=files,
        trace_root=trace_root,
        run_id=run_id,
    )
    mutation_gate = _mutation_gate(files)
    benchmark_gate = _seeded_benchmark_gate(benchmark_root)

    gates = [
        CIGateResult(
            name="unsupported-construct-gate",
            passed=not unsupported_failures,
            details="ok" if not unsupported_failures else "; ".join(sorted(unsupported_failures)),
        ),
        CIGateResult(
            name="obligation-policy-gate",
            passed=not determinism_failures,
            details="ok" if not determinism_failures else "; ".join(sorted(determinism_failures)),
        ),
        CIGateResult(
            name="assumption-evidence-gate",
            passed=not assumption_failures,
            details="ok" if not assumption_failures else "; ".join(sorted(assumption_failures)),
        ),
        CIGateResult(
            name="semantic-guard-gate",
            passed=not semantic_failures,
            details="ok" if not semantic_failures else "; ".join(sorted(semantic_failures)),
        ),
        CIGateResult(
            name="proof-gate",
            passed=not proof_failures,
            details="ok" if not proof_failures else "; ".join(sorted(proof_failures)),
        ),
        CIGateResult(
            name="verdict-contract-gate",
            passed=not verdict_failures,
            details="ok" if not verdict_failures else "; ".join(sorted(verdict_failures)),
        ),
        trace_gate,
        CIGateResult(
            name="reproducibility-gate",
            passed=not reproducibility_failures,
            details="ok"
            if not reproducibility_failures
            else "; ".join(sorted(reproducibility_failures)),
        ),
        mutation_gate,
        benchmark_gate,
    ]
    return CIGateReport(
        passed=all(item.passed for item in gates),
        gates=gates,
    )


def _traceability_gate(
    files: Sequence[Tuple[str, str]],
    trace_root: Path,
    run_id: str | None,
) -> CIGateResult:
    if not run_id:
        return CIGateResult(
            name="traceability-gate",
            passed=False,
            details="pipeline did not expose run_id",
        )

    run_dir = trace_root / run_id
    missing: List[str] = []
    if not (run_dir / "manifest.json").exists():
        missing.append("manifest.json")
    if not (run_dir / "summary.json").exists():
        missing.append("summary.json")

    for filename, _ in files:
        base = run_dir / "files" / filename
        for required in ("01_discovery.json", "result.json"):
            if not (base / required).exists():
                missing.append(f"{filename}:{required}")

        discovery_path = base / "01_discovery.json"
        unsupported = True
        if discovery_path.exists():
            try:
                payload = json.loads(discovery_path.read_text(encoding="utf-8"))
                unsupported = bool(payload.get("unsupported_constructs", []))
            except Exception:
                missing.append(f"{filename}:01_discovery.json_unreadable")

        if not unsupported:
            translation_exists = (base / "02_translation.lean").exists() or (base / "02_translation.dfy").exists()
            if not translation_exists:
                missing.append(f"{filename}:02_translation.*")
            if not (base / "03_verify_stdout.txt").exists():
                missing.append(f"{filename}:03_verify_stdout.txt")

    return CIGateResult(
        name="traceability-gate",
        passed=not missing,
        details="ok" if not missing else "; ".join(sorted(missing)),
    )


def _mutation_gate(files: Sequence[Tuple[str, str]]) -> CIGateResult:
    failures: List[str] = []
    for filename, code in files:
        gate = mutation_kill_rate_gate(
            original_code=code,
            evaluate_mutation=_evaluate_mutation,
            minimum_kill_rate=0.95,
        )
        if not gate.passed:
            failures.append(f"{filename}:{gate.details}")
    return CIGateResult(
        name="mutation-gate",
        passed=not failures,
        details="ok" if not failures else "; ".join(sorted(failures)),
    )


def _seeded_benchmark_gate(benchmark_root: Path | None) -> CIGateResult:
    if benchmark_root is None:
        return CIGateResult(
            name="seeded-benchmark-gate",
            passed=False,
            details="benchmark root is not configured",
        )

    manifest_path = benchmark_root / "manifest.json"
    if not manifest_path.exists():
        return CIGateResult(
            name="seeded-benchmark-gate",
            passed=False,
            details="benchmarks/seeded/manifest.json missing",
        )

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return CIGateResult(
            name="seeded-benchmark-gate",
            passed=False,
            details=f"invalid manifest: {exc}",
        )

    policy = ObligationPolicy()
    ast_translator = ASTTranslator()
    failures: List[str] = []
    for case in manifest.get("cases", []):
        rel_path = case.get("path")
        expected = case.get("expected")
        if not rel_path or not expected:
            failures.append("manifest_case_missing_path_or_expected")
            continue
        path = benchmark_root / rel_path
        if not path.exists():
            failures.append(f"missing_case:{rel_path}")
            continue

        code = path.read_text(encoding="utf-8")
        derived = policy.derive(code)

        if expected == "blocking":
            if not (derived.obligations or derived.unsupported_constructs):
                failures.append(f"{rel_path}:expected_blocking")
        elif expected == "supported":
            if derived.unsupported_constructs:
                failures.append(f"{rel_path}:unexpected_unsupported")
        elif expected == "semantic_guard_failure":
            translation = ast_translator.translate(code, derived.obligations, [])
            if not translation.success:
                failures.append(f"{rel_path}:translation_failed")
            else:
                guard = run_semantic_guard(code, translation.code, derived.obligations)
                if guard.passed:
                    failures.append(f"{rel_path}:expected_guard_failure")
        else:
            failures.append(f"{rel_path}:unknown_expected:{expected}")

    return CIGateResult(
        name="seeded-benchmark-gate",
        passed=not failures,
        details="ok" if not failures else "; ".join(sorted(failures)),
    )


def _evaluate_mutation(mutated_code: str) -> Verdict:
    policy = ObligationPolicy().derive(mutated_code)
    if policy.unsupported_constructs:
        return Verdict.UNVERIFIED
    if not policy.obligations:
        return Verdict.VERIFIED

    if _contains_loop(mutated_code):
        translation = DafnyTranslator().translate(mutated_code, policy.obligations, [])
    else:
        translation = ASTTranslator().translate(mutated_code, policy.obligations, [])

    if not translation.success:
        return Verdict.UNVERIFIED

    guard = run_semantic_guard(mutated_code, translation.code, policy.obligations)
    if not guard.passed:
        return Verdict.UNVERIFIED
    return Verdict.VULNERABLE


def _contains_loop(code: str) -> bool:
    return "for " in code or "while " in code
