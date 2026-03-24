from unittest.mock import MagicMock, patch

from src.core.models import Verdict
from src.core.quality_gates import generate_simple_mutations, mutation_kill_rate_gate


def test_generate_simple_mutations_produces_variants() -> None:
    code = "if amount >= 0:\n    return balance\n"
    variants = generate_simple_mutations(code)
    assert variants
    assert any(variant != code for variant in variants)


def test_mutation_kill_rate_gate_passes_with_strict_evaluator() -> None:
    # Provide original_verdict=VERIFIED explicitly so that the evaluator returning
    # VULNERABLE for every mutation is correctly counted as "killing" each one.
    code = "if amount >= 0:\n    return balance\n"

    def evaluator(_mutated: str) -> Verdict:
        return Verdict.VULNERABLE

    result = mutation_kill_rate_gate(
        code,
        evaluate_mutation=evaluator,
        minimum_kill_rate=0.95,
        original_verdict=Verdict.VERIFIED,
    )
    assert result.passed
    assert "rate=" in result.details
    assert "base=VERIFIED" in result.details


def test_mutation_kill_rate_gate_fails_with_weak_evaluator() -> None:
    code = "if amount >= 0:\n    return balance\n"

    def evaluator(_mutated: str) -> Verdict:
        return Verdict.VERIFIED

    result = mutation_kill_rate_gate(code, evaluate_mutation=evaluator, minimum_kill_rate=0.95)
    assert not result.passed


def test_no_mutation_tied_to_specific_variable_name() -> None:
    """No generated mutation should depend on a hardcoded variable name like 'balance'."""
    code = "if x >= 0:\n    return x\n"
    mutations = generate_simple_mutations(code)
    # The old implementation had a mutation tied to "return balance".
    # With the new implementation every mutation is a generic operator/keyword swap,
    # so every mutation must be derivable purely from operators present in the code.
    for m in mutations:
        assert "balance" not in m
        assert "amount" not in m


def test_evaluate_mutation_with_lean_routes_to_dafny_for_loops() -> None:
    """When code contains a loop, _evaluate_mutation_with_lean must use DafnyVerifier."""
    from src.core.ci_integrity import _evaluate_mutation_with_lean

    loop_code = (
        "def total(items: list[int]) -> int:\n"
        "    s = 0\n"
        "    for x in items:\n"
        "        s += x\n"
        "    return s\n"
    )

    mock_translation = MagicMock()
    mock_translation.success = True
    mock_translation.code = "-- mock dafny code"

    mock_dafny_result = MagicMock()
    mock_dafny_result.verification_error = False
    mock_dafny_result.obligation_results = [MagicMock(verified=True)]

    mock_lean_result = MagicMock()
    mock_lean_result.verification_error = False
    mock_lean_result.obligation_results = [MagicMock(verified=True)]

    with patch("src.core.ci_integrity.DafnyTranslator") as MockDafnyTrans, \
         patch("src.core.ci_integrity.DafnyVerifier") as MockDafny, \
         patch("src.core.ci_integrity.LeanVerifier") as MockLean:
        MockDafnyTrans.return_value.translate.return_value = mock_translation
        MockDafny.return_value.verify.return_value = mock_dafny_result
        MockLean.return_value.verify.return_value = mock_lean_result

        _evaluate_mutation_with_lean(loop_code)

        MockDafny.assert_called_once_with(require_docker=False)
        MockDafny.return_value.verify.assert_called_once()
        MockLean.return_value.verify.assert_not_called()


def test_evaluate_mutation_with_lean_routes_to_lean_for_non_loops() -> None:
    """When code has no loop, _evaluate_mutation_with_lean must use LeanVerifier."""
    from src.core.ci_integrity import _evaluate_mutation_with_lean

    non_loop_code = (
        "def withdraw(balance: int, amount: int) -> int:\n"
        "    if amount > balance:\n"
        "        return balance\n"
        "    return balance - amount\n"
    )

    mock_translation = MagicMock()
    mock_translation.success = True
    mock_translation.code = "-- mock lean code"

    mock_lean_result = MagicMock()
    mock_lean_result.verification_error = False
    mock_lean_result.obligation_results = [MagicMock(verified=True)]

    with patch("src.core.ci_integrity.ASTTranslator") as MockASTTrans, \
         patch("src.core.ci_integrity.DafnyVerifier") as MockDafny, \
         patch("src.core.ci_integrity.LeanVerifier") as MockLean:
        MockASTTrans.return_value.translate.return_value = mock_translation
        MockLean.return_value.verify.return_value = mock_lean_result

        _evaluate_mutation_with_lean(non_loop_code)

        MockLean.assert_called_once_with(require_docker=False)
        MockLean.return_value.verify.assert_called_once()
        MockDafny.return_value.verify.assert_not_called()

