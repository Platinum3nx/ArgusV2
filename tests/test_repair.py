from src.core.models import Obligation
from src.core.repair import RepairEngine


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeModels:
    def generate_content(self, model: str, contents: str) -> _FakeResponse:
        assert "Verification error" in contents
        return _FakeResponse("def withdraw(balance, amount):\n    return balance")


class _FakeClient:
    def __init__(self, api_key: str) -> None:
        self.models = _FakeModels()


def test_repair_engine_generates_fix(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test")
    monkeypatch.setattr("src.core.repair.genai.Client", _FakeClient)

    obligations = [
        Obligation(
            id="withdraw:non_negative_result",
            property="withdraw(...) >= 0",
            category="non_negativity",
            description="non-negative",
        )
    ]
    result = RepairEngine(max_attempts=1).repair(
        python_code="def withdraw(balance, amount): return balance - amount",
        error_message="proof failed",
        obligations=obligations,
    )
    assert result.success
    assert "return balance" in (result.fixed_code or "")

