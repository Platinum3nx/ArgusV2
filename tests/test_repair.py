from src.core.llm_provider import LLMClient
from src.core.models import Obligation
from src.core.repair import RepairEngine


class _FakeLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def generate(self, contents: str) -> str:
        assert "Verification error" in contents
        return "def withdraw(balance, amount):\n    return balance"


def test_repair_engine_generates_fix() -> None:
    obligations = [
        Obligation(
            id="withdraw:non_negative_result",
            property="withdraw(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]
    result = RepairEngine(llm_client=_FakeLLMClient(), max_attempts=1).repair(
        python_code="def withdraw(balance, amount): return balance - amount",
        error_message="proof failed",
        obligations=obligations,
    )
    assert result.success
    assert "return balance" in (result.fixed_code or "")
