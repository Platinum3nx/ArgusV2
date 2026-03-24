from typing import Iterable

from src.core.llm_provider import LLMClient
from src.core.models import Obligation
from src.core.repair import RepairEngine


class _SequencedLLMClient(LLMClient):
    provider_name = "fake"
    model_id = "fake-model"

    def __init__(self, responses: Iterable[str], expected_snippets: Iterable[str] = ()) -> None:
        self.responses = list(responses)
        self.prompts: list[str] = []
        self.expected_snippets = list(expected_snippets)

    def generate(self, contents: str) -> str:
        self.prompts.append(contents)
        for snippet in self.expected_snippets:
            assert snippet in contents
        if not self.responses:
            raise AssertionError("No more responses configured")
        return self.responses.pop(0)


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
    result = RepairEngine(
        llm_client=_SequencedLLMClient(
            [
                "```python\ndef withdraw(balance, amount):\n    return balance\n```",
            ],
            expected_snippets=(
                "Preserve the existing function signatures",
                "Do not use unsupported constructs such as `raise`",
                "Do not wrap the answer in markdown fences",
            ),
        ),
        max_attempts=1,
    ).repair(
        python_code="def withdraw(balance, amount): return balance - amount",
        error_message="proof failed",
        obligations=_obligations(),
    )
    assert result.success
    assert "return balance" in (result.fixed_code or "")
    assert result.fixed_code == "def withdraw(balance, amount):\n    return balance"


def test_repair_engine_empty_response_returns_no_fix() -> None:
    result = RepairEngine(llm_client=_EmptyLLMClient(), max_attempts=1).repair(
        python_code="def withdraw(balance, amount): return balance - amount",
        error_message="proof failed",
        obligations=_obligations(),
    )
    assert not result.success
    assert result.fixed_code is None


def test_repair_engine_retries_after_invalid_subset_then_succeeds() -> None:
    client = _SequencedLLMClient(
        [
            "def withdraw(balance, amount):\n    raise ValueError('Insufficient funds')",
            "def withdraw(balance, amount):\n    return balance",
        ]
    )
    result = RepairEngine(llm_client=client, max_attempts=2).repair(
        python_code="def withdraw(balance, amount): return balance - amount",
        error_message="proof failed",
        obligations=_obligations(),
    )

    assert result.success
    assert result.fixed_code == "def withdraw(balance, amount):\n    return balance"
    assert len(result.attempts) == 2
    assert not result.attempts[0].success
    assert "unsupported Python subset" in result.attempts[0].error
    assert len(client.prompts) == 2
    assert "Previous attempt failed validation" in client.prompts[1]


def test_repair_engine_rejects_signature_changes() -> None:
    result = RepairEngine(
        llm_client=_SequencedLLMClient([
            "def withdraw(balance):\n    return balance",
        ]),
        max_attempts=1,
    ).repair(
        python_code="def withdraw(balance, amount): return balance - amount",
        error_message="proof failed",
        obligations=_obligations(),
    )

    assert not result.success
    assert result.fixed_code is None
    assert len(result.attempts) == 1
    assert "signature" in result.attempts[0].error


def test_repair_engine_exception_propagation_returns_no_fix() -> None:
    result = RepairEngine(llm_client=_ExceptionLLMClient(), max_attempts=1).repair(
        python_code="def withdraw(balance, amount): return balance - amount",
        error_message="proof failed",
        obligations=_obligations(),
    )
    assert not result.success
    assert result.fixed_code is None
