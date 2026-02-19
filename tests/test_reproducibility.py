from src.core.quality_gates import obligation_determinism_gate


def test_obligation_determinism_gate_passes_for_stable_policy() -> None:
    code = """
def withdraw(balance: int, amount: int) -> int:
    return balance - amount
"""
    result = obligation_determinism_gate(code, runs=5)
    assert result.passed

