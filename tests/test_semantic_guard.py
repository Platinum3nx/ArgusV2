from src.core.models import Obligation
from src.core.semantic_guard import run_semantic_guard


def test_semantic_guard_detects_sorry() -> None:
    obligations = [
        Obligation(
            id="withdraw:non_negative_result",
            property="withdraw(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]
    result = run_semantic_guard(
        python_code="def withdraw(balance, amount): return balance - amount",
        translated_code="theorem withdraw_safe := by sorry",
        obligations=obligations,
    )
    assert not result.passed
    assert any(issue.code == "PROOF_SORRY" for issue in result.issues)


def test_semantic_guard_passes_for_expected_encoding() -> None:
    obligations = [
        Obligation(
            id="withdraw:non_negative_result",
            property="withdraw(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]
    translated = """
def withdraw (balance amount : Int) : Int := balance - amount
theorem withdraw_safe (balance amount : Int) : withdraw balance amount >= 0 := by
  omega
"""
    result = run_semantic_guard(
        python_code="def withdraw(balance, amount): return balance - amount",
        translated_code=translated,
        obligations=obligations,
    )
    assert result.passed


def test_semantic_guard_detects_missing_function_symbol() -> None:
    obligations = [
        Obligation(
            id="f:bounds_safe_access",
            property="bounds safe",
            category="bounds",
            description="bounds",
        )
    ]
    result = run_semantic_guard(
        python_code="def f(items, i): return items[i]",
        translated_code="def g (items : List Int) (i : Int) := items[i]!",
        obligations=obligations,
    )
    assert not result.passed
    assert any(issue.code == "MISSING_FUNCTION_SYMBOL" for issue in result.issues)

