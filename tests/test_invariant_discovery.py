from src.core.invariant_discovery import InvariantDiscovery


def test_invariant_discovery_returns_policy_obligations_without_llm() -> None:
    code = """
def withdraw(balance: int, amount: int) -> int:
    return balance - amount
"""
    discovery = InvariantDiscovery(use_llm=False)
    result = discovery.discover(code)
    assert result.obligations
    assert result.assumptions_valid

