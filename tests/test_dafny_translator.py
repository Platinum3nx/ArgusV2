from src.core.models import Obligation
from src.core.translator.dafny_translator import DafnyTranslator


def test_dafny_translator_translates_range_loop_deterministically() -> None:
    code = """
def total(balance: int, amount: int) -> int:
    s = 0
    for i in range(amount):
        s += 1
    return balance - s
"""
    obligations = [
        Obligation(
            id="total:non_negative_result",
            property="total(...) >= 0",
            category="non_negativity",
            description="non-negative",
        ),
        Obligation(
            id="total:loop_progress_and_safety",
            property="loop progress",
            category="loop_invariant",
            description="loop safety",
        ),
    ]
    outcome = DafnyTranslator().translate(code, obligations, [])
    assert outcome.success
    assert "method total(" in outcome.code
    assert "ensures result >= 0" in outcome.code
    assert "while (__argus_idx_i < amount)" in outcome.code
    assert "invariant 0 <= __argus_idx_i <= amount" in outcome.code
    assert "decreases amount - __argus_idx_i" in outcome.code


def test_dafny_translator_fails_for_unsupported_category() -> None:
    code = """
def f(state: int) -> int:
    i = 0
    while i < 1:
        i += 1
    return state
"""
    obligations = [
        Obligation(
            id="f:valid_state_transition",
            property="state transitions remain within policy",
            category="state_transition",
            description="state transition",
        )
    ]
    outcome = DafnyTranslator().translate(code, obligations, [])
    assert not outcome.success
    assert "Unsupported obligation categories" in outcome.error


def test_dafny_translator_uses_ir_path_for_non_loop_code() -> None:
    code = """
def inc(x: int) -> int:
    return x + 1
"""
    obligations = [
        Obligation(
            id="inc:non_negative_result",
            property="inc(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]
    outcome = DafnyTranslator().translate(code, obligations, [])
    assert outcome.success
    assert "method inc(" in outcome.code
    assert "result := (x + 1);" in outcome.code


def test_dafny_translator_translates_while_loop_with_decreases() -> None:
    code = """
def climb(n: int) -> int:
    i = 0
    while i < n:
        i += 1
    return i
"""
    obligations = [
        Obligation(
            id="climb:loop_progress_and_safety",
            property="Loop preserves invariants and terminates",
            category="loop_invariant",
            description="loop safety",
        )
    ]
    outcome = DafnyTranslator().translate(code, obligations, [])
    assert outcome.success
    assert "while ((i < n))" in outcome.code
    assert "invariant true" in outcome.code
    assert "decreases n - i" in outcome.code
