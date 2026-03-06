from src.core.equivalence import run_equivalence_check


def test_equivalence_passes_for_simple_arithmetic() -> None:
    code = """
def withdraw(balance: int, amount: int) -> int:
    if amount > balance:
        return balance
    return balance - amount
"""
    result = run_equivalence_check(code, trials_per_function=32, seed=9)
    assert result.passed
    assert result.cases_checked > 0


def test_equivalence_detects_index_semantic_drift() -> None:
    code = """
def pick(items: list[int], i: int) -> int:
    return items[i]
"""
    result = run_equivalence_check(code, trials_per_function=64, seed=3)
    assert not result.passed
    assert any(issue.function == "pick" for issue in result.issues)
