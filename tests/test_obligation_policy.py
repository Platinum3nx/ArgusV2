from src.core.obligation_policy import ObligationPolicy


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


def test_obligation_hash_is_deterministic() -> None:
    code = """
def add_product_id(existing_ids: list[int], new_id: int) -> list[int]:
    return existing_ids + [new_id]
"""
    policy = ObligationPolicy()
    result_1 = policy.derive(code)
    result_2 = policy.derive(code)
    assert result_1.canonical_hash() == result_2.canonical_hash()

