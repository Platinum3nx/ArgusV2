from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List

from .assumption_evidence import validate_assumptions
from .models import AssumedInput, Verdict
from .obligation_policy import ObligationPolicy


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    details: str


def obligation_determinism_gate(
    python_code: str,
    policy: ObligationPolicy | None = None,
    runs: int = 3,
) -> GateResult:
    policy = policy or ObligationPolicy()
    hashes = [policy.derive(python_code).canonical_hash() for _ in range(runs)]
    passed = len(set(hashes)) == 1
    return GateResult(
        name="obligation-determinism",
        passed=passed,
        details=f"hashes={hashes}",
    )


def assumption_coverage_gate(assumptions: Iterable[AssumedInput]) -> GateResult:
    ok, issues = validate_assumptions(assumptions)
    details = "all assumptions evidenced" if ok else "; ".join(
        f"{item.property}:{item.reason}" for item in issues
    )
    return GateResult(name="assumption-evidence-coverage", passed=ok, details=details)


def unsupported_fail_closed_gate(verdict: Verdict, unsupported_constructs: List[str]) -> GateResult:
    if not unsupported_constructs:
        return GateResult(
            name="unsupported-fail-closed",
            passed=True,
            details="no unsupported constructs present",
        )
    passed = verdict == Verdict.UNVERIFIED
    return GateResult(
        name="unsupported-fail-closed",
        passed=passed,
        details=f"unsupported={unsupported_constructs}, verdict={verdict.value}",
    )


def mutation_kill_rate_gate(
    original_code: str,
    evaluate_mutation: Callable[[str], Verdict],
    minimum_kill_rate: float = 0.95,
    original_verdict: Verdict | None = None,
) -> GateResult:
    """
    Compute the mutation kill rate for a piece of code.

    A mutation is considered "killed" when its verdict DIFFERS from the original
    verdict (i.e., the verification pipeline detected the semantic change).
    If ``original_verdict`` is not provided, it is computed via ``evaluate_mutation``.
    """
    mutations = generate_simple_mutations(original_code)
    if not mutations:
        return GateResult(
            name="mutation-kill-rate",
            passed=True,
            details="skipped: no mutations generated",
        )

    base_verdict = original_verdict if original_verdict is not None else evaluate_mutation(original_code)

    killed = 0
    for mutated in mutations:
        verdict = evaluate_mutation(mutated)
        if verdict != base_verdict:
            killed += 1

    rate = killed / len(mutations)
    passed = rate >= minimum_kill_rate
    return GateResult(
        name="mutation-kill-rate",
        passed=passed,
        details=f"killed={killed}/{len(mutations)} rate={rate:.3f} base={base_verdict.value}",
    )


def generate_simple_mutations(code: str) -> List[str]:
    mutations: List[str] = []
    replacements = [
        (">=", ">"),
        ("<=", "<"),
        ("==", "!="),
        ("return balance", "return balance - amount"),
        ("if ", "if not "),
    ]
    for source, target in replacements:
        if source in code:
            mutations.append(code.replace(source, target, 1))
    return mutations

