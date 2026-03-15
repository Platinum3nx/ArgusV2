from src.core.obligation_policy import ObligationPolicy
from src.core.models import Severity


def test_obligation_policy_generates_expected_core_obligations() -> None:
    code = """
def withdraw(balance: int, amount: int) -> int:
    return balance - amount
"""
    result = ObligationPolicy().derive(code)
    ids = {item.id for item in result.obligations}
    assert "withdraw:non_negative_result" in ids
    assert result.unsupported_constructs == []


def test_obligation_policy_adds_bounds_for_subscript() -> None:
    code = """
def get_item(items: list[int], i: int) -> int:
    return items[i]
"""
    result = ObligationPolicy().derive(code)
    ids = {item.id for item in result.obligations}
    assert "get_item:bounds_safe_access" in ids


def test_obligation_policy_marks_unsupported_constructs() -> None:
    code = """
class Account:
    pass

async def worker():
    return 1
"""
    result = ObligationPolicy().derive(code)
    assert "class_definition" in result.unsupported_constructs
    assert "async_function" in result.unsupported_constructs


def test_derive_preconditions_injects_nonneg_hypotheses_for_numeric_params() -> None:
    code = """
def withdraw(balance: int, amount: int) -> int:
    if amount > balance:
        return balance
    return balance - amount
"""
    policy = ObligationPolicy()
    result = policy.derive(code)
    preconditions = policy.derive_preconditions(code, result.obligations)

    props = {p.property for p in preconditions}
    assert "balance >= 0" in props
    assert "amount >= 0" in props

    # All generated preconditions must be structurally valid
    for pc in preconditions:
        assert pc.source_type == "policy"
        assert pc.justification
        assert pc.source_ref
        assert pc.evidence_id
        assert pc.severity == Severity.HIGH


def test_derive_preconditions_returns_empty_when_no_nonneg_obligation() -> None:
    code = """
def add_item(items: list[int], value: int) -> list[int]:
    return items + [value]
"""
    policy = ObligationPolicy()
    result = policy.derive(code)
    # Only uniqueness obligation present, no non_negativity
    nonneg = [o for o in result.obligations if o.category == "non_negativity"]
    assert not nonneg
    preconditions = policy.derive_preconditions(code, result.obligations)
    assert preconditions == []


def test_derive_preconditions_skips_non_int_params() -> None:
    code = """
def check(flag: bool, value: int) -> int:
    return value
"""
    policy = ObligationPolicy()
    result = policy.derive(code)
    preconditions = policy.derive_preconditions(code, result.obligations)
    props = {p.property for p in preconditions}
    # bool param should not generate a precondition
    assert "flag >= 0" not in props


def test_derive_preconditions_no_duplicates_when_called_twice() -> None:
    code = """
def withdraw(balance: int, amount: int) -> int:
    return balance - amount
"""
    policy = ObligationPolicy()
    result = policy.derive(code)
    preconditions = policy.derive_preconditions(code, result.obligations)
    props = [p.property for p in preconditions]
    assert len(props) == len(set(props)), "Duplicate precondition properties generated"


def test_obligation_hash_is_deterministic() -> None:
    code = """
def add_product_id(existing_ids: list[int], new_id: int) -> list[int]:
    return existing_ids + [new_id]
"""
    policy = ObligationPolicy()
    result_1 = policy.derive(code)
    result_2 = policy.derive(code)
    assert result_1.canonical_hash() == result_2.canonical_hash()

