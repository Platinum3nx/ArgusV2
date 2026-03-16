from src.core.invariant_discovery import InvariantDiscovery
from src.core.llm_provider import LLMClient

_WITHDRAW_CODE = """
def withdraw(balance: int, amount: int) -> int:
    return balance - amount
"""


class _MalformedLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        return "this is not json at all ##%^& garbage"


class _ExceptionLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        raise RuntimeError("API timeout")


def test_invariant_discovery_returns_policy_obligations_without_llm() -> None:
    discovery = InvariantDiscovery(use_llm=False)
    result = discovery.discover(_WITHDRAW_CODE)
    assert result.obligations
    assert result.assumptions_valid


def test_discovery_malformed_llm_output_returns_no_llm_assumptions() -> None:
    discovery = InvariantDiscovery(llm_client=_MalformedLLMClient(), use_llm=True)
    result = discovery.discover(_WITHDRAW_CODE)
    # Deterministic obligations from policy must still be present
    assert result.obligations
    # Malformed JSON produces no parsed assumptions
    assert result.assumed_inputs == []


def test_discovery_exception_propagation_returns_no_llm_assumptions() -> None:
    discovery = InvariantDiscovery(llm_client=_ExceptionLLMClient(), use_llm=True)
    result = discovery.discover(_WITHDRAW_CODE)
    # Deterministic obligations from policy must still be present
    assert result.obligations
    # Exception is caught; no LLM assumptions, no false VERIFIED
    assert result.assumed_inputs == []

