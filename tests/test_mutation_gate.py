from src.core.models import Verdict
from src.core.quality_gates import generate_simple_mutations, mutation_kill_rate_gate


def test_generate_simple_mutations_produces_variants() -> None:
    code = "if amount >= 0:\n    return balance\n"
    variants = generate_simple_mutations(code)
    assert variants
    assert any(variant != code for variant in variants)


def test_mutation_kill_rate_gate_passes_with_strict_evaluator() -> None:
    code = "if amount >= 0:\n    return balance\n"

    def evaluator(_mutated: str) -> Verdict:
        return Verdict.VULNERABLE

    result = mutation_kill_rate_gate(code, evaluate_mutation=evaluator, minimum_kill_rate=0.95)
    assert result.passed
    assert "rate=" in result.details


def test_mutation_kill_rate_gate_fails_with_weak_evaluator() -> None:
    code = "if amount >= 0:\n    return balance\n"

    def evaluator(_mutated: str) -> Verdict:
        return Verdict.VERIFIED

    result = mutation_kill_rate_gate(code, evaluate_mutation=evaluator, minimum_kill_rate=0.95)
    assert not result.passed

