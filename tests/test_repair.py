from src.core.llm_provider import LLMClient
from src.core.models import Obligation
from src.core.repair import RepairEngine


class _FakeLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        assert "Verification error" in contents
        return "def withdraw(balance, amount):\n    return balance"


class _EmptyLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        return ""


class _ExceptionLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        raise RuntimeError("API timeout")


def _obligations() -> list:
    return [
        Obligation(
            id="withdraw:non_negative_result",
            property="withdraw(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]


def test_repair_engine_generates_fix() -> None:
    result = RepairEngine(llm_client=_FakeLLMClient(), max_attempts=1).repair(
        python_code="def withdraw(balance, amount): return balance - amount",
        error_message="proof failed",
        obligations=_obligations(),
    )
    assert result.success
    assert "return balance" in (result.fixed_code or "")


def test_repair_engine_empty_response_returns_no_fix() -> None:
    result = RepairEngine(llm_client=_EmptyLLMClient(), max_attempts=1).repair(
        python_code="def withdraw(balance, amount): return balance - amount",
        error_message="proof failed",
        obligations=_obligations(),
    )
    assert not result.success
    assert result.fixed_code is None


def test_repair_engine_exception_propagation_returns_no_fix() -> None:
    result = RepairEngine(llm_client=_ExceptionLLMClient(), max_attempts=1).repair(
        python_code="def withdraw(balance, amount): return balance - amount",
        error_message="proof failed",
        obligations=_obligations(),
    )
    assert not result.success
    assert result.fixed_code is None
