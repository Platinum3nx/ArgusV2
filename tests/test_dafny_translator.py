from src.core.models import AssumedInput, Obligation
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


def test_dafny_translator_includes_requires_for_assumptions() -> None:
    code = """
def climb(n: int) -> int:
    i = 0
    while i < n:
        i += 1
    return i
"""
    obligations = [
        Obligation(
            id="climb:non_negative_result",
            property="climb(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]
    assumptions = [
        AssumedInput(
            property="n >= 0",
            description="input is non-negative",
            justification="domain constraint",
            source_type="documentation",
            source_ref="spec:input_constraints",
            evidence_id="ev-001",
        ),
    ]
    outcome = DafnyTranslator().translate(code, obligations, assumptions)
    assert outcome.success
    assert "requires n >= 0" in outcome.code
    assert "ensures result >= 0" in outcome.code


def test_dafny_translator_loop_fallback_includes_requires_for_assumptions() -> None:
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
    ]
    assumptions = [
        AssumedInput(
            property="balance >= 0",
            description="balance is non-negative",
            justification="domain constraint",
            source_type="documentation",
            source_ref="spec:balance_constraints",
            evidence_id="ev-002",
        ),
        AssumedInput(
            property="amount >= 0",
            description="amount is non-negative",
            justification="domain constraint",
            source_type="documentation",
            source_ref="spec:amount_constraints",
            evidence_id="ev-003",
        ),
    ]
    outcome = DafnyTranslator().translate(code, obligations, assumptions)
    assert outcome.success
    assert "requires balance >= 0" in outcome.code
    assert "requires amount >= 0" in outcome.code
    assert "ensures result >= 0" in outcome.code


def test_dafny_translator_scopes_assumptions_to_matching_function_params() -> None:
    code = """
def withdraw(balance: int, amount: int) -> int:
    total = balance
    while total > amount:
        total -= 1
    return total - amount

def deposit(value: int, count: int) -> int:
    total = value
    while count > 0:
        total += 1
        count -= 1
    return total
"""
    obligations = [
        Obligation(
            id="withdraw:loop_progress_and_safety",
            property="withdraw loop progress",
            category="loop_invariant",
            description="loop safety",
        ),
        Obligation(
            id="withdraw:non_negative_result",
            property="withdraw(...) >= 0",
            category="non_negativity",
            description="non-negative",
        ),
        Obligation(
            id="deposit:loop_progress_and_safety",
            property="deposit loop progress",
            category="loop_invariant",
            description="loop safety",
        ),
        Obligation(
            id="deposit:non_negative_result",
            property="deposit(...) >= 0",
            category="non_negativity",
            description="non-negative",
        ),
    ]
    assumptions = [
        AssumedInput(
            property="balance >= 0",
            description="balance is non-negative",
            justification="domain constraint",
            source_type="documentation",
            source_ref="spec:balance",
            evidence_id="ev-balance",
        ),
        AssumedInput(
            property="amount >= 0",
            description="amount is non-negative",
            justification="domain constraint",
            source_type="documentation",
            source_ref="spec:amount",
            evidence_id="ev-amount",
        ),
        AssumedInput(
            property="value >= 0",
            description="value is non-negative",
            justification="domain constraint",
            source_type="documentation",
            source_ref="spec:value",
            evidence_id="ev-value",
        ),
        AssumedInput(
            property="count >= 0",
            description="count is non-negative",
            justification="domain constraint",
            source_type="documentation",
            source_ref="spec:count",
            evidence_id="ev-count",
        ),
    ]

    outcome = DafnyTranslator().translate(code, obligations, assumptions)
    assert outcome.success

    withdraw_section, deposit_section = outcome.code.split("method deposit", 1)
    deposit_section = "method deposit" + deposit_section

    assert "requires balance >= 0" in withdraw_section
    assert "requires amount >= 0" in withdraw_section
    assert "requires value >= 0" not in withdraw_section
    assert "requires count >= 0" not in withdraw_section

    assert "requires value >= 0" in deposit_section
    assert "requires count >= 0" in deposit_section
    assert "requires balance >= 0" not in deposit_section
    assert "requires amount >= 0" not in deposit_section
